from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.database.database_factory import (
    load_database_from_id,
    load_database_from_name,
)
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.singleton import singleton

if TYPE_CHECKING:
    from notionary import NotionDatabase


@singleton
class NotionDatabaseProvider(LoggingMixin):
    """
    Provider class for creating and caching Notion database instances.

    Prevents duplicate database creation when working with multiple pages from the same database.
    Each Notion page references its parent database to determine selectable properties and options.
    By caching database instances, this provider avoids excessive network requests when reading options,
    significantly improving performance for repeated property lookups across many pages.
    """

    def __init__(self):
        self._database_cache: dict[str, NotionDatabase] = {}

    async def get_database_by_id(self, database_id: str, force_refresh: bool = False) -> NotionDatabase:
        """Get a NotionDatabase by ID with caching."""
        cache_key = self._create_id_cache_key(database_id)

        if self._should_use_cache(cache_key, force_refresh):
            self.logger.debug(f"Using cached database for ID: {database_id}")
            return self._database_cache[cache_key]

        database = await load_database_from_id(database_id)
        self._cache_database(database)
        return database

    async def get_database_by_name(
        self,
        database_name: str,
        min_similarity: float = 0.6,
        force_refresh: bool = False,
    ) -> NotionDatabase:
        """Get a NotionDatabase by name with caching."""
        name_cache_key = self._create_name_cache_key(database_name)

        if self._should_use_cache(name_cache_key, force_refresh):
            return self._database_cache[name_cache_key]

        database = await load_database_from_name(database_name, min_similarity)

        id_cache_key = self._create_id_cache_key(database.id)
        if not force_refresh and id_cache_key in self._database_cache:
            self.logger.debug(f"Found existing cached database by ID: {database.id}")
            existing_database = self._database_cache[id_cache_key]

            self._database_cache[name_cache_key] = existing_database
            return existing_database

        self._cache_database(database, database_name)
        self.logger.debug(f"Cached database: {database.title} (ID: {database.id})")

        return database

    def invalidate_database_cache(self, database_id: str) -> bool:
        """
        Simply invalidate (remove) cache entries for a database without reloading.

        Args:
            database_id: The database ID to invalidate

        Returns:
            True if cache entries were found and removed, False otherwise
        """
        id_cache_key = self._create_id_cache_key(database_id)
        was_cached = id_cache_key in self._database_cache

        if not was_cached:
            self.logger.debug(f"No cache entry found for database ID: {database_id}")
            return False

        removed_database = self._database_cache.pop(id_cache_key)
        self.logger.debug(f"Invalidated cached database: {removed_database.title}")

        name_keys_to_remove = [
            cache_key
            for cache_key, cached_db in self._database_cache.items()
            if (cache_key.startswith("name:") and cached_db.id == database_id)
        ]

        for name_key in name_keys_to_remove:
            self._database_cache.pop(name_key)
            self.logger.debug(f"Invalidated name-based cache: {name_key}")

        return was_cached

    def _should_use_cache(self, cache_key: str, force_refresh: bool) -> bool:
        """Returns True if the cache should be used for the given cache_key."""
        return not force_refresh and cache_key in self._database_cache

    def _cache_database(
        self,
        database: NotionDatabase,
        original_name: str | None = None,
    ) -> None:
        """Cache a database by both ID and name (if provided)."""
        # Always cache by ID
        id_cache_key = self._create_id_cache_key(database.id)
        self._database_cache[id_cache_key] = database

        if original_name:
            name_cache_key = self._create_name_cache_key(original_name)
            self._database_cache[name_cache_key] = database

    def _create_id_cache_key(self, database_id: str) -> str:
        """Create cache key for database ID."""
        return f"id:{database_id}"

    def _create_name_cache_key(self, database_name: str) -> str:
        """Create cache key for database name."""
        return f"name:{database_name.lower().strip()}"
