import difflib
from typing import Protocol


class HasTitle(Protocol):
    title: str


def fuzzy_suggestions(query: str, items: list[HasTitle], top_n: int = 5) -> list[str]:
    scored = [
        (item, difflib.SequenceMatcher(None, query.lower(), item.title.lower()).ratio())
        for item in items
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [item.title for item, score in scored[:top_n] if score >= 0.6]
