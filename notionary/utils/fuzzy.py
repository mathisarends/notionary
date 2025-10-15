import difflib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class _MatchResult(Generic[T]):
    item: T
    similarity: float


def find_best_match(
    query: str,
    items: list[T],
    text_extractor: Callable[[T], str],
    min_similarity: float,
) -> T | None:
    matches = _find_best_matches(query, items, text_extractor, min_similarity, limit=1)
    return matches[0].item if matches else None


def find_all_matches(
    query: str,
    items: list[T],
    text_extractor: Callable[[T], str],
    min_similarity: float,
) -> list[T]:
    matches = _find_best_matches(query, items, text_extractor, min_similarity, limit=None)
    return [match.item for match in matches]


def _find_best_matches(
    query: str,
    items: list[T],
    text_extractor: Callable[[T], str],
    min_similarity: float = 0.0,
    limit: int | None = None,
) -> list[_MatchResult[T]]:
    results = []

    for item in items:
        text = text_extractor(item)
        similarity = _calculate_similarity(query, text)

        if similarity >= min_similarity:
            results.append(_MatchResult(item=item, similarity=similarity))

    results = _sort_by_highest_similarity_first(results)

    if limit:
        return results[:limit]

    return results


def _sort_by_highest_similarity_first(results: list[_MatchResult]) -> list[_MatchResult]:
    return sorted(results, key=lambda x: x.similarity, reverse=True)


def _calculate_similarity(query: str, target: str) -> float:
    return difflib.SequenceMatcher(
        isjunk=None,
        a=query.lower().strip(),
        b=target.lower().strip(),
    ).ratio()
