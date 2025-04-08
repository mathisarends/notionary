from typing import Optional
from notionary.core.notion_client import NotionClient


class DatabaseInfoService:
    """Service für den Zugriff auf Datenbankinformationen"""

    def __init__(self, client: NotionClient, database_id: str):
        self._client = client
        self.database_id = database_id
        self._title = None

    async def fetch_database_title(self) -> str:
        """
        Fetch the database title from the Notion API.

        Returns:
            The database title or "Untitled" if no title is found
        """
        db_details = await self._client.get(f"databases/{self.database_id}")
        if not db_details:
            return "Untitled"

        title = "Untitled"
        if "title" in db_details:
            title_parts = []
            for text_obj in db_details["title"]:
                if "plain_text" in text_obj:
                    title_parts.append(text_obj["plain_text"])

            if title_parts:
                title = "".join(title_parts)

        return title

    @property
    def title(self) -> Optional[str]:
        return self._title

    async def load_title(self) -> str:
        """Lädt den Titel der Datenbank und speichert ihn im Cache"""
        self._title = await self.fetch_database_title()
        return self._title
