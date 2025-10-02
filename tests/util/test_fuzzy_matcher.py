from dataclasses import dataclass

import pytest

from notionary.utils.fuzzy import _calculate_similarity, _find_best_matches, find_best_match


@dataclass
class SampleItem:
    name: str
    title: str


class TestFuzzyMatcher:
    @pytest.fixture
    def sample_items(self) -> list[SampleItem]:
        """Sample test data with various similarity patterns."""
        return [
            SampleItem(name="apple", title="Apple Inc."),
            SampleItem(name="application", title="Mobile Application"),
            SampleItem(name="banana", title="Banana Republic"),
            SampleItem(name="grape", title="Grape Fruit Company"),
            SampleItem(name="orange", title="Orange County"),
            SampleItem(name="pineapple", title="Pineapple Express"),
            SampleItem(name="app", title="App Store"),
        ]

    def test_find_best_match_exact_match(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("apple", sample_items, lambda x: x.name)

        assert result is not None
        assert result.name == "apple"

    def test_find_best_match_partial_match(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("app", sample_items, lambda x: x.name)

        assert result is not None
        assert result.name == "app"  # Should find exact "app" over partial "apple"

    def test_find_best_match_case_insensitive(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("APPLE", sample_items, lambda x: x.name)

        assert result is not None
        assert result.name == "apple"

    def test_find_best_match_with_title_extractor(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("Mobile App", sample_items, lambda x: x.title)

        assert result is not None
        assert result.title == "Mobile Application"

    def test_find_best_match_no_match_below_threshold(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("xyz", sample_items, lambda x: x.name, min_similarity=0.5)

        assert result is None

    def test_find_best_match_no_match_with_high_threshold(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("appl", sample_items, lambda x: x.name, min_similarity=0.9)

        assert result is None

    def test_find_best_match_empty_list(self) -> None:
        result = find_best_match("apple", [], lambda x: x.name)

        assert result is None

    def test_find_best_match_empty_query(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("", sample_items, lambda x: x.name)

        # Should return first item as all have 0 similarity with empty string
        assert result is not None

    def test_find_best_matches_multiple_results(self, sample_items: list[SampleItem]) -> None:
        results = _find_best_matches("app", sample_items, lambda x: x.name, min_similarity=0.3, limit=3)

        assert len(results) <= 3
        assert len(results) > 0
        # Results should be sorted by similarity (highest first)
        for i in range(len(results) - 1):
            assert results[i].similarity >= results[i + 1].similarity

    def test_find_best_matches_with_limit(self, sample_items: list[SampleItem]) -> None:
        results = _find_best_matches("a", sample_items, lambda x: x.name, min_similarity=0.1, limit=2)

        assert len(results) <= 2

    def test_find_best_matches_no_limit(self, sample_items: list[SampleItem]) -> None:
        results = _find_best_matches("a", sample_items, lambda x: x.name, min_similarity=0.1)

        assert len(results) > 0
        for result in results:
            assert result.similarity >= 0.1

    def test_calculate_similarity_identical_strings(self) -> None:
        similarity = _calculate_similarity("apple", "apple")
        assert similarity == pytest.approx(1.0)

    def test_calculate_similarity_completely_different(self) -> None:
        similarity = _calculate_similarity("apple", "xyz")
        assert 0.0 <= similarity < 0.3

    def test_calculate_similarity_case_insensitive(self) -> None:
        similarity1 = _calculate_similarity("Apple", "apple")
        similarity2 = _calculate_similarity("APPLE", "apple")

        assert similarity1 == pytest.approx(1.0)
        assert similarity2 == pytest.approx(1.0)

    def test_calculate_similarity_with_whitespace(self) -> None:
        similarity = _calculate_similarity("  apple  ", "apple")
        assert similarity == pytest.approx(1.0)

    def test_find_best_match_with_none_min_similarity(self, sample_items: list[SampleItem]) -> None:
        result = find_best_match("xyz", sample_items, lambda x: x.name, min_similarity=None)

        assert result is not None

    def test_find_best_matches_sorted_by_similarity(self) -> None:
        items = [
            SampleItem(name="apple", title="Apple"),
            SampleItem(name="application", title="Application"),
            SampleItem(name="app", title="App"),
            SampleItem(name="apricot", title="Apricot"),
        ]

        results = _find_best_matches("app", items, lambda x: x.name, min_similarity=0.0)

        for i in range(len(results) - 1):
            assert results[i].similarity >= results[i + 1].similarity

        assert results[0].item.name == "app"

    def test_text_extractor_function(self) -> None:
        items = [
            SampleItem(name="short", title="Very Long Title Here"),
            SampleItem(name="very_long_name_here", title="Short"),
        ]

        # Using name extractor
        result1 = find_best_match("long", items, lambda x: x.name)
        assert result1.name == "very_long_name_here"

        # Using title extractor
        result2 = find_best_match("long", items, lambda x: x.title)
        assert result2.title == "Very Long Title Here"
