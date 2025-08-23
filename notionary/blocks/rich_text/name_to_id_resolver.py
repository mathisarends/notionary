from __future__ import annotations

import re
import difflib
from typing import Optional

from notionary import NotionPage, NotionWorkspace

class NameIdResolver:
    """
    Bidirectional resolver for Notion page names and IDs.
    
    Supports:
    - Name → ID: Search workspace and find best fuzzy match
    - ID → Name: Fetch page by ID and extract title
    """
    
    _NOTION_ID_RE = re.compile(
        r"^[0-9a-f]{32}$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        search_limit: int = 10,
        match_threshold: float = 0.72,  # 0.0 to 1.0, minimum similarity for fuzzy match
    ):
        """
        Initialize the resolver with a Notion workspace.
        """
        self.workspace = NotionWorkspace(token=token)
        self.search_limit = search_limit
        self.match_threshold = match_threshold

    async def resolve_id(self, page_name: str) -> Optional[str]:
        """
        Convert a page name to its Notion ID.
        
        Strategy:
        1. Check if input is already a valid Notion ID
        2. Search workspace for pages matching the name
        3. Find best fuzzy match using title similarity
        
        Args:
            page_name: Human-readable page name to resolve
            
        Returns:
            Notion page ID if found, None otherwise
        """
        if not page_name:
            return None

        cleaned_name = page_name.strip()
        
        # Return if already a valid Notion ID
        if self._is_notion_id(cleaned_name):
            return cleaned_name

        # Search workspace for matching pages
        search_results = await self.workspace.search_pages(
            query=cleaned_name, 
            limit=self.search_limit
        )
        
        # Find best match using fuzzy matching on titles
        page_titles = [self._extract_page_title(page) for page in search_results]
        best_match_id = self._find_best_fuzzy_match(
            query=cleaned_name, 
            candidate_titles=page_titles, 
            candidate_pages=search_results
        )
        
        return best_match_id

    async def resolve_name(self, page_id: str) -> Optional[str]:
        """
        Convert a Notion page ID to its human-readable name.
        
        Args:
            page_id: Notion page ID to resolve
            
        Returns:
            Page title/name if found, None if page doesn't exist or is inaccessible
        """
        if not page_id or not self._is_notion_id(page_id):
            return None
            
        try:
            page = await NotionPage.from_page_id(page_id)
            return self._extract_page_title(page)
        except Exception:
            # Page not found, not accessible, or other error
            return None

    def _find_best_fuzzy_match(
        self, 
        query: str, 
        candidate_titles: list[str], 
        candidate_pages: list[NotionPage]
    ) -> Optional[str]:
        """
        Find the best fuzzy match among candidate page titles.
        
        Uses difflib.SequenceMatcher to calculate similarity scores and returns
        the page ID of the best match if it meets the threshold.
        
        Args:
            query: The search query to match against
            candidate_titles: List of page titles to compare
            candidate_pages: Corresponding NotionPage objects
            
        Returns:
            Page ID of best match, or None if no match meets threshold
        """
        if not candidate_titles:
            return None

        best_score = -1.0
        best_index = None
        normalized_query = query.casefold()
        
        # Find highest similarity score
        for i, title in enumerate(candidate_titles):
            score = difflib.SequenceMatcher(
                a=normalized_query, 
                b=title.casefold()
            ).ratio()
            
            if score > best_score:
                best_score = score
                best_index = i

        # Return best match if it meets threshold
        if best_index is not None and best_score >= self.match_threshold:
            return candidate_pages[best_index].id

        # Fallback: try exact case-insensitive match
        try:
            normalized_titles = [title.casefold() for title in candidate_titles]
            exact_index = normalized_titles.index(normalized_query)
            return candidate_pages[exact_index].id
        except ValueError:
            return None

    def _extract_page_title(self, page: NotionPage) -> str:
        """
        Extract the title from a NotionPage object.
        
        Uses the page's built-in title property which handles the underlying
        title parsing from Notion's block structure.
        
        Args:
            page: NotionPage instance
            
        Returns:
            Page title as string, empty string if no title
        """
        return page.title or ""

    @classmethod
    def _is_notion_id(cls, text: str) -> bool:
        """
        Check if a text string matches Notion ID format.
        
        Supports both formats:
        - 32 hex characters: abc123def456...
        - UUID with dashes: abc123de-f456-7890-abcd-ef1234567890
        
        Args:
            text: String to check
            
        Returns:
            True if text matches Notion ID format, False otherwise
        """
        cleaned_text = text.replace("_", "").strip()
        return bool(cls._NOTION_ID_RE.match(cleaned_text))