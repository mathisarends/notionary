import os
from enum import Enum
from abc import ABC
from typing import Dict, Any, Optional, Union, Callable, TypeVar, Awaitable
import functools
import asyncio
import atexit

import aiohttp
from dotenv import load_dotenv

from notionary.util.logging_mixin import LoggingMixin

load_dotenv()

T = TypeVar('T')

class HttpMethod(Enum):
    """HTTP methods enum for API requests."""
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


def ensure_session(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """Dekorator, der sicherstellt, dass eine Session vorhanden ist."""
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers, timeout=self.timeout)
            self._register_session_for_cleanup()
        return await func(self, *args, **kwargs)
    return wrapper


def handle_errors(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[Dict[str, Any]]]:
    """Dekorator für einheitliche Fehlerbehandlung."""
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except aiohttp.ClientResponseError as e:
            self.logger.error("API request failed: %s", str(e))
            return {"error": f"API request failed: {str(e)}", "status": e.status}
        except aiohttp.ClientError as e:
            self.logger.error("Connection error: %s", str(e))
            return {"error": f"Connection error: {str(e)}"}
        except asyncio.TimeoutError:
            self.logger.error("Request timed out")
            return {"error": "Request timed out"}
        except Exception as e:
            self.logger.error("Unexpected error: %s", str(e))
            return {"error": f"Unexpected error: {str(e)}"}
    return wrapper


class AbstractNotionClient(ABC, LoggingMixin):
    """Abstract base class for Notion API interactions."""
    
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    _active_sessions = set()  # Klassen-Variable, um alle aktiven Sessions zu verfolgen
    
    @classmethod
    async def _cleanup_sessions(cls):
        """Schließe alle offenen Sessions."""
        for session in list(cls._active_sessions):
            if not session.closed:
                await session.close()
        cls._active_sessions.clear()
    
    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        self.token = token or os.getenv("NOTION_SECRET", "")
        if not self.token:
            raise ValueError("Notion API token is required. Set NOTION_SECRET environment variable or pass token to constructor.")
        
        # Set up headers for all requests
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION
        }
        
        # Session will be initialized when needed
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        # Stellen sicher, dass wir eine Cleanup-Methode beim Programmende haben
        self._setup_global_cleanup()
    
    def _setup_global_cleanup(self):
        """Registriere die globalen Session-Cleanup-Funktionen."""
        # Diese Funktion wird nur einmal ausgeführt
        if not hasattr(AbstractNotionClient, '_cleanup_registered'):
            # Für synchrones Beenden
            atexit.register(lambda: asyncio.run(AbstractNotionClient._cleanup_sessions()))
            
            # Für asyncio Event-Loop-Beenden
            try:
                loop = asyncio.get_event_loop()
                loop.add_signal_handler(15, lambda: asyncio.create_task(AbstractNotionClient._cleanup_sessions()))  # SIGTERM
            except (NotImplementedError, RuntimeError):
                # Ignorieren, falls in Windows oder keine Event-Loop verfügbar
                pass
            
            AbstractNotionClient._cleanup_registered = True
    
    def _register_session_for_cleanup(self):
        """Registriere die aktuelle Session für das Cleanup."""
        if self.session and not self.session.closed:
            AbstractNotionClient._active_sessions.add(self.session)
    
    async def __aenter__(self):
        """Context manager entry point."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers, timeout=self.timeout)
            self._register_session_for_cleanup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        if self.session and not self.session.closed:
            await self.session.close()
            if self.session in AbstractNotionClient._active_sessions:
                AbstractNotionClient._active_sessions.remove(self.session)
            self.session = None
    
    async def close(self):
        """Explicit method to close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
            if self.session in AbstractNotionClient._active_sessions:
                AbstractNotionClient._active_sessions.remove(self.session)
            self.session = None
    
    @ensure_session
    @handle_errors
    async def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Generischer HTTP-Request-Handler.
        
        Args:
            method: HTTP-Methode ('get', 'post', etc.)
            url: Ziel-URL
            **kwargs: Zusätzliche Parameter für die Request-Methode
            
        Returns:
            Dict mit der JSON-Antwort
        """
        http_method = getattr(self.session, method)
        
        self.logger.debug("Making %s request to %s", method.upper(), url)
        
        async with http_method(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _make_request(self, method: Union[HttpMethod, str], endpoint: str, 
                        data: Optional[Dict[str, Any]] = None, 
                        fail_silently: bool = False) -> Dict[str, Any]:
        """
        General method for API requests with improved error handling.
        
        Args:
            method: HTTP method as enum or string
            endpoint: API endpoint (without base URL)
            data: Optional JSON data for POST/PATCH requests
            fail_silently: If True, returns empty dict on error instead of raising exception
            
        Returns:
            Dict with API response or empty dict if failed silently
            
        Raises:
            NotionRequestError: If request fails and fail_silently is False
        """
        # Build the URL and normalize the method
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        if isinstance(method, HttpMethod):
            method_str = method.value
        else:
            method_str = str(method).lower()
        
        # Check if method is valid
        if method_str not in [m.value for m in HttpMethod]:
            raise ValueError(f"Unsupported method: {method_str}")
        
        kwargs = {}
        if data is not None and method_str in [HttpMethod.POST.value, HttpMethod.PATCH.value]:
            kwargs["json"] = data
            
        response = await self._request(method_str, url, **kwargs)
        
        # Centralized error handling
        if response is None or "error" in response:
            error_msg = response.get('error', 'Unknown error') if response else 'No response'
            error_msg = f"Error in {method_str.upper()} {endpoint}: {error_msg}"
            self.logger.error(error_msg)
            
            if fail_silently:
                return {}
            else:
                raise NotionRequestError(error_msg, response)
                
        return response
    
    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get a page by ID."""
        return await self._make_request(HttpMethod.GET, f"pages/{page_id}")
    
    async def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update page properties."""
        return await self._make_request(HttpMethod.PATCH, f"pages/{page_id}", {"properties": properties})