from typing import Dict, Optional
from notionary.database.notion_database import NotionDatabase
from notionary.util import singleton, LoggingMixin


@singleton
class NotionDatabaseFactory(LoggingMixin):
    """
    Factory class for creating and caching Notion database instances.
    Prevents duplicate database creation when working with multiple pages from the same database.
    """

    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self._database_cache: Dict[str, NotionDatabase] = {}

    async def get_database_by_id(
        self, database_id: str, token: Optional[str] = None, force_refresh: bool = False
    ) -> NotionDatabase:
        """
        Get a NotionDatabase by ID with caching.
        """
        if self._should_use_cache(database_id, force_refresh):
            self.logger.debug(f"Using cached database for ID: {database_id}")
            return self._database_cache[database_id]

        database = await NotionDatabase.from_database_id(database_id, token)

        if self.cache_enabled:
            self._database_cache[database_id] = database
            self.logger.debug(f"Cached database: {database.title} (ID: {database_id})")
        return database

    async def get_database_by_name(
        self,
        database_name: str,
        token: Optional[str] = None,
        min_similarity: float = 0.6,
        force_refresh: bool = False,
    ) -> NotionDatabase:
        """
        Get a NotionDatabase by name with caching.
        """
        # Erst nach Name suchen, dann ID als Cache-Key verwenden
        database = await NotionDatabase.from_database_name(
            database_name, token, min_similarity
        )
        database_id = database.database_id
        if self._should_use_cache(database_id, force_refresh):
            self.logger.debug(
                f"Using cached database for name: {database_name} (ID: {database_id})"
            )
            return self._database_cache[database_id]
        if self.cache_enabled:
            self._database_cache[database_id] = database
            self.logger.debug(f"Cached database: {database.title} (ID: {database_id})")
        return database

    def get_cached_database(self, database_id: str) -> Optional[NotionDatabase]:
        """
        Get a database from cache without creating a new one.
        """
        if not self.cache_enabled:
            return None
        return self._database_cache.get(database_id)

    def _should_use_cache(self, database_id: str, force_refresh: bool) -> bool:
        """
        Returns True if the cache should be used for the given database_id.
        """
        is_cached = self._is_cached(database_id)
        return not force_refresh and self.cache_enabled and is_cached

    def _is_cached(self, database_id: str) -> bool:
        """
        Check if a database is cached.
        """
        return database_id in self._database_cache
