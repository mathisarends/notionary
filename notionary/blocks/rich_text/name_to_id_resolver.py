from __future__ import annotations

import re
import difflib
from typing import Optional

from notionary import NotionPage, NotionWorkspace

_NOTION_ID_RE = re.compile(
    r"^[0-9a-f]{32}$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _looks_like_notion_id(text: str) -> bool:
    return bool(_NOTION_ID_RE.match(text.replace("_", "").strip()))


class NameToIdResolver:
    """
    Auflösung natürlicher Namen -> Notion-IDs.
    - Pages: globale Suche + Fuzzy-Match
    - Users: nur via Aliases / 'me' / direkte ID (API kann nicht global nach Name suchen)
    """

    def __init__(
        self,
        workspace: NotionWorkspace,
        user_aliases: Optional[dict[str, str]] = None,  # name_lower -> user_id
        page_aliases: Optional[dict[str, str]] = None,  # name_lower -> page_id
        page_search_limit: int = 10,
        page_match_threshold: float = 0.72,  # 0..1, ab wann ein Fuzzy-Match akzeptiert wird
    ):
        self.workspace = workspace
        self.user_aliases = {k.casefold(): v for k, v in (user_aliases or {}).items()}
        self.page_aliases = {k.casefold(): v for k, v in (page_aliases or {}).items()}
        self.page_search_limit = page_search_limit
        self.page_match_threshold = page_match_threshold

    # ---------------------------
    # Public API
    # ---------------------------

    async def resolve_page(self, name: str) -> Optional[str]:
        """
        Versucht, eine Page-ID aus einem natürlichen Namen zu bestimmen.
        Strategie:
          1) direkte ID?
          2) Alias-Treffer?
          3) Notion-Suche + Fuzzy-Match auf Page-Titel
        """
        if not name:
            return None

        n = name.strip()
        if _looks_like_notion_id(n):
            return n

        # Alias
        alias_hit = self.page_aliases.get(n.casefold())
        if alias_hit:
            return alias_hit

        # Suche
        pages = await self.workspace.search_pages(query=n, limit=self.page_search_limit)
        candidate_titles = [_safe_title(p) for p in pages]
        best_id = self._best_fuzzy_match(n, candidate_titles, pages)
        return best_id

    async def resolve_user(self, name: str) -> Optional[str]:
        """
        Versucht, eine User-ID aus einem natürlichen Namen zu bestimmen.
        Strategie:
          1) direkte ID?
          2) 'me'/'bot'/('ich') -> aktueller Bot-User
          3) Alias (lokales Mapping)
        Hinweis: Globale Usersuche ist mit der Notion-API hier nicht verfügbar.
        """
        if not name:
            return None

        n = name.strip()
        if _looks_like_notion_id(n):
            return n

        # Sonderfälle
        if n.casefold() in {"me", "bot", "current", "ich"}:
            bot = await self.workspace.get_current_bot_user()
            return bot.id if isinstance(bot, NotionUser) else None

        # Alias
        alias_hit = self.user_aliases.get(n.casefold())
        if alias_hit:
            return alias_hit

        # Kein globaler Fallback möglich (API-Limit)
        return None

    # ---------------------------
    # Internals
    # ---------------------------

    def _best_fuzzy_match(
        self, query: str, titles: list[str], pages: list[NotionPage]
    ) -> Optional[str]:
        """
        Nimmt den besten difflib-Match über Page-Titel, prüft Schwelle, gibt Page-ID zurück.
        """
        if not titles:
            return None

        # difflib liefert 0..1 Ähnlichkeit über get_close_matches, aber ohne Score.
        # Daher nutzen wir SequenceMatcher ratio pro Kandidat, um Schwelle zu prüfen.
        best_score: float = -1.0
        best_idx: Optional[int] = None

        q = query.casefold()
        for i, title in enumerate(titles):
            score = difflib.SequenceMatcher(a=q, b=title.casefold()).ratio()
            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx is not None and best_score >= self.page_match_threshold:
            return pages[best_idx].id

        # exakte (case-insensitive) Fallback-Prüfung, falls Schwelle nicht erreicht
        try:
            exact_idx = [t.casefold() for t in titles].index(q)
            return pages[exact_idx].id
        except ValueError:
            return None


def _safe_title(page: NotionPage) -> str:
    # Passe an deine Page-API an; sollte robust einen Titelstring extrahieren.
    # Häufig: page.properties["title"].title[0].plain_text, aber dein Wrapper abstrahiert das ggf.
    return (
        (getattr(page, "title", None) or "").strip() or getattr(page, "name", "") or ""
    )
