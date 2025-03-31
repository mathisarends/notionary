import os
from enum import Enum
from abc import ABC
from typing import Dict, Any, Optional, Union
import httpx
from dotenv import load_dotenv

class HttpMethod(Enum):
    """Enum für HTTP-Methoden."""
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"

class NotionClient(ABC):
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    
    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        """Initialisiert den Notion-Client mit Token und Timeout."""
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
    
    async def get(self, endpoint: str) -> Dict[str, Any]:
        return await self._make_request(HttpMethod.GET, endpoint)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._make_request(HttpMethod.POST, endpoint, data)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._make_request(HttpMethod.PATCH, endpoint, data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        return await self._make_request(HttpMethod.DELETE, endpoint)
    
    async def _make_request(self, method: Union[HttpMethod, str], endpoint: str, 
                        data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Performs an HTTP request to the specified endpoint."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        method_str = method.value if isinstance(method, HttpMethod) else str(method).lower()
        
        try:
            if method_str in [HttpMethod.POST.value, HttpMethod.PATCH.value] and data is not None:
                response = await getattr(self.client, method_str)(url, json=data)
            else:
                response = await getattr(self.client, method_str)(url)
                
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP status error: {e.response.status_code}", "status": e.response.status_code}
        except httpx.RequestError as e:
            return {"error": f"Request error: {str(e)}"}