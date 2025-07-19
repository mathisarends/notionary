from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING
from notionary.database.client import NotionDatabaseClient
from notionary.exceptions.database_exceptions import DatabaseNotFoundException
from notionary.models.notion_database_response import NotionDatabaseResponse
from notionary.util import LoggingMixin, FuzzyMatcher, format_uuid
from notionary.util.singleton_metaclass import SingletonMetaClass

if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionDatabaseProvider(LoggingMixin, metaclass=SingletonMetaClass):
    """
    Provider class for creating and caching Notion database instances.
    Prevents duplicate database creation when working with multiple pages from the same database.
    """

    def __init__(self):
        self._database_cache: Dict[str, NotionDatabase] = {}

    async def get_database_by_id(
        self, database_id: str, token: Optional[str] = None, force_refresh: bool = False
    ) -> NotionDatabase:
        """Get a NotionDatabase by ID with caching."""
        cache_key = self._create_id_cache_key(database_id)

        if self._should_use_cache(cache_key, force_refresh):
            self.logger.debug(f"Using cached database for ID: {database_id}")
            return self._database_cache[cache_key]

        database = await self._create_from_database_id(database_id, token)
        self._cache_database(database, token)
        return database

    async def get_database_by_name(
        self,
        database_name: str,
        token: Optional[str] = None,
        min_similarity: float = 0.6,
        force_refresh: bool = False,
    ) -> NotionDatabase:
        """Get a NotionDatabase by name with caching."""
        name_cache_key = self._create_name_cache_key(database_name, token)

        if self._should_use_cache(name_cache_key, force_refresh):
            return self._database_cache[name_cache_key]

        database = await self._create_from_database_name(
            database_name, token, min_similarity
        )

        id_cache_key = self._create_id_cache_key(database.database_id)
        if not force_refresh and id_cache_key in self._database_cache:
            self.logger.debug(
                f"Found existing cached database by ID: {database.database_id}"
            )
            existing_database = self._database_cache[id_cache_key]

            self._database_cache[name_cache_key] = existing_database
            return existing_database

        self._cache_database(database, token, database_name)
        self.logger.debug(
            f"Cached database: {database.title} (ID: {database.database_id})"
        )

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
            if (cache_key.startswith("name:") and cached_db.database_id == database_id)
        ]

        for name_key in name_keys_to_remove:
            self._database_cache.pop(name_key)
            self.logger.debug(f"Invalidated name-based cache: {name_key}")

        return was_cached

    async def _create_from_database_id(
        self, database_id: str, token: Optional[str]
    ) -> NotionDatabase:
        """Create a NotionDatabase from database ID via API."""
        formatted_id = format_uuid(database_id) or database_id

        async with NotionDatabaseClient(token=token) as client:
            db_response = await client.get_database(formatted_id)
            return self._create_from_response(db_response, token)

    async def _create_from_database_name(
        self,
        database_name: str,
        token: Optional[str] = None,
        min_similarity: float = 0.6,
    ) -> NotionDatabase:
        """Create a NotionDatabase by finding it via name with fuzzy matching."""
        async with NotionDatabaseClient(token=token) as client:
            search_result = await client.search_databases(database_name, limit=10)

            if not search_result.results:
                self.logger.warning("No databases found for name: %s", database_name)
                raise DatabaseNotFoundException(database_name)

            best_match = FuzzyMatcher.find_best_match(
                query=database_name,
                items=search_result.results,
                text_extractor=lambda db: self._extract_title(db),
                min_similarity=min_similarity,
            )

            if not best_match:
                available_titles = [
                    self._extract_title(db) for db in search_result.results[:5]
                ]
                self.logger.warning(
                    "No sufficiently similar database found for '%s' (min: %.3f). Available: %s",
                    database_name,
                    min_similarity,
                    available_titles,
                )
                raise DatabaseNotFoundException(database_name)

            database_id = best_match.item.id
            db_response = await client.get_database(database_id=database_id)
            instance = self._create_from_response(db_response, token)

            self.logger.info(
                "Created database: '%s' (ID: %s, similarity: %.3f)",
                instance.title,
                database_id,
                best_match.similarity,
            )

            return instance

    def _should_use_cache(self, cache_key: str, force_refresh: bool) -> bool:
        """Returns True if the cache should be used for the given cache_key."""
        return not force_refresh and cache_key in self._database_cache

    def _cache_database(
        self,
        database: NotionDatabase,
        token: Optional[str],
        original_name: Optional[str] = None,
    ) -> None:
        """Cache a database by both ID and name (if provided)."""
        # Always cache by ID
        id_cache_key = self._create_id_cache_key(database.database_id)
        self._database_cache[id_cache_key] = database

        if original_name:
            name_cache_key = self._create_name_cache_key(original_name, token)
            self._database_cache[name_cache_key] = database

    def _create_id_cache_key(self, database_id: str) -> str:
        """Create cache key for database ID."""
        return f"id:{database_id}"

    def _create_name_cache_key(self, database_name: str, token: Optional[str]) -> str:
        """Create cache key for database name."""
        token_suffix = f":{hash(token)}" if token else ":default"
        return f"name:{database_name.lower().strip()}{token_suffix}"

    def _create_from_response(
        self, db_response: NotionDatabaseResponse, token: Optional[str]
    ) -> NotionDatabase:
        """Create NotionDatabase instance from API response."""
        from notionary import NotionDatabase

        title = self._extract_title(db_response)
        emoji_icon = self._extract_emoji_icon(db_response)

        instance = NotionDatabase(
            database_id=db_response.id,
            title=title,
            url=db_response.url,
            emoji_icon=emoji_icon,
            properties=db_response.properties,
            token=token,
        )

        self.logger.info(
            "Created database manager: '%s' (ID: %s)", title, db_response.id
        )

        return instance

    def _extract_title(self, db_response: NotionDatabaseResponse) -> str:
        """Extract title from database response."""
        if db_response.title and len(db_response.title) > 0:
            return db_response.title[0].plain_text
        return "Untitled Database"

    def _extract_emoji_icon(self, db_response: NotionDatabaseResponse) -> Optional[str]:
        """Extract emoji from database response."""
        if not db_response.icon:
            return None

        if db_response.icon.type == "emoji":
            return db_response.icon.emoji

        return None
