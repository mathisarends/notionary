import os
from enum import Enum
from abc import ABC
from typing import Dict, Any, Optional, Union
import httpx
from dotenv import load_dotenv

class HttpMethod(Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"

class NotionClient(ABC):
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
        
        self.client = None
        self.timeout = timeout
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def _ensure_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)
            
    async def _make_request(self, method: Union[HttpMethod, str], endpoint: str, 
                        data: Optional[Dict[str, Any]] = None):
        await self._ensure_client()
        
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        method_str = method.value if isinstance(method, HttpMethod) else str(method).lower()
        
        try:
            if method_str in [HttpMethod.POST.value, HttpMethod.PATCH.value] and data is not None:
                response = await getattr(self.client, method_str)(url, json=data)
            else:
                response = await getattr(self.client, method_str)(url)
                
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}