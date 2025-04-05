import os
from enum import Enum
from typing import Dict, Any, Optional, Union
import httpx
from dotenv import load_dotenv
from notionary.util.logging_mixin import LoggingMixin


class HttpMethod(Enum):
    """Enum für HTTP-Methoden."""
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class RequestResult:
    """Klasse zur Kapselung des Ergebnisses einer API-Anfrage."""
    
    def __init__(self, success: bool, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None, 
                 status_code: Optional[int] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.status_code = status_code
    
    def __bool__(self):
        """Erlaubt die Verwendung von if result: für Erfolgsprüfung."""
        return self.success
    
    def __str__(self):
        if self.success:
            return f"Success: {self.data}"
        return f"Error: {self.error} (Status: {self.status_code})"


class NotionClient(LoggingMixin):
    """Verbesserter Notion-Client mit besserer Fehlerbehandlung."""
    
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    
    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        load_dotenv()
        self.token = token or os.getenv("NOTION_SECRET", "")
        if not self.token:
            raise ValueError("Notion API token is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION
        }
        
        self.client = httpx.AsyncClient(
            headers=self.headers, 
            timeout=timeout
        )
    
    async def close(self):
        if self.client:
            await self.client.aclose()
    
    # TODO: vllt. macht es hier eh Sinn die API hier so zu designen, dass hier immer nur die Daten zurückgegeben werden den Status interessiert doch nicht wirklich
    async def get(self, endpoint: str) -> RequestResult:
        return await self._make_request(HttpMethod.GET, endpoint)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> RequestResult:
        return await self._make_request(HttpMethod.POST, endpoint, data)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> RequestResult:
        return await self._make_request(HttpMethod.PATCH, endpoint, data)
    
    async def delete(self, endpoint: str) -> RequestResult:
        return await self._make_request(HttpMethod.DELETE, endpoint)
    
    
    async def api_get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        High-level abstraction for GET requests that returns the data directly.
        """
        result = await self.get(endpoint)
        
        if not result:
            self.logger.error("API error (GET %s): %s", endpoint, result.error)
            return None
        
        return result.data

    async def api_patch(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        High-level abstraction for PATCH requests that returns the data directly.
        """
        result = await self.patch(endpoint, data)
        
        if not result:
            self.logger.error("API error (PATCH %s): %s", endpoint, result.error)
            return None
        
        return result.data

    async def api_post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        High-level abstraction for POST requests that returns the data directly.
        """
        result = await self.post(endpoint, data)
        
        if not result:
            self.logger.error("API error (POST %s): %s", endpoint, result.error)
            return None
        
        return result.data

    async def api_delete(self, endpoint: str) -> bool:
        """
        High-level abstraction for DELETE requests.
        """
        result = await self.delete(endpoint)
        
        if not result:
            self.logger.error("API error (DELETE %s): %s", endpoint, result.error)
            return False
        
        return True
        
    async def _make_request(self, method: Union[HttpMethod, str], endpoint: str,
                        data: Optional[Dict[str, Any]] = None) -> RequestResult:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        method_str = method.value if isinstance(method, HttpMethod) else str(method).lower()
        
        try:
            self.logger.debug("Sending %s request to %s", method_str.upper(), url)
            
            if method_str in [HttpMethod.POST.value, HttpMethod.PATCH.value] and data is not None:
                response = await getattr(self.client, method_str)(url, json=data)
            else:
                response = await getattr(self.client, method_str)(url)
            
            response.raise_for_status()
            result_data = response.json()
            self.logger.debug("Request successful: %s", url)
            return RequestResult(success=True, data=result_data, status_code=response.status_code)
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP status error: {e.response.status_code} - {e.response.text}"
            self.logger.error("Request failed (%s): %s", url, error_msg)
            return RequestResult(
                success=False,
                error=error_msg,
                status_code=e.response.status_code
            )
            
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            self.logger.error("Request error (%s): %s", url, error_msg)
            return RequestResult(success=False, error=error_msg)
    