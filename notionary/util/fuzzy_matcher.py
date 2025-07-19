from __future__ import annotations
import difflib
from typing import List, Any, TypeVar, Callable, Optional
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class MatchResult:
    """Result of a fuzzy match operation."""
    item: Any
    similarity: float
    matched_text: str

class FuzzyMatcher:
    """Utility class for fuzzy string matching operations."""
    
    @staticmethod
    def calculate_similarity(query: str, target: str) -> float:
        """Calculate similarity between two strings using difflib."""
        return difflib.SequenceMatcher(
            None, 
            query.lower().strip(), 
            target.lower().strip()
        ).ratio()
    
    @classmethod
    def find_best_matches(
        cls,
        query: str,
        items: List[T],
        text_extractor: Callable[[T], str],
        min_similarity: float = 0.0,
        limit: Optional[int] = None
    ) -> List[MatchResult[T]]:
        """
        Find best fuzzy matches from a list of items.
        
        Args:
            query: The search query
            items: List of items to search through
            text_extractor: Function to extract text from each item
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            limit: Maximum number of results to return
            
        Returns:
            List of MatchResult objects sorted by similarity (highest first)
        """
        results = []
        
        for item in items:
            text = text_extractor(item)
            similarity = cls.calculate_similarity(query, text)
            
            if similarity >= min_similarity:
                results.append(MatchResult(
                    item=item,
                    similarity=similarity,
                    matched_text=text
                ))
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x.similarity, reverse=True)
        
        # Apply limit if specified
        if limit:
            results = results[:limit]
            
        return results
    
    @classmethod
    def find_best_match(
        cls,
        query: str,
        items: List[T],
        text_extractor: Callable[[T], str],
        min_similarity: float = 0.0
    ) -> Optional[MatchResult[T]]:
        """Find the single best fuzzy match."""
        matches = cls.find_best_matches(
            query, items, text_extractor, min_similarity, limit=1
        )
        return matches[0] if matches else None