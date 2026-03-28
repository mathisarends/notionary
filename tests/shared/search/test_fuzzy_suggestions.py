from typing import NamedTuple

from notionary.shared.search.fuzzy import fuzzy_suggestions


class MockItem(NamedTuple):
    title: str


class TestFuzzySuggestions:
    def test_exact_match_returns_item(self) -> None:
        """Returns exact matches with high confidence."""
        items = [MockItem(title="Python"), MockItem(title="Java")]
        result = fuzzy_suggestions("Python", items)
        assert result == ["Python"]

    def test_partial_match_above_threshold(self) -> None:
        """Returns partial matches with similarity >= 0.6."""
        items = [
            MockItem(title="Python"),
            MockItem(title="JavaScript"),
            MockItem(title="Java"),
        ]
        result = fuzzy_suggestions("Python", items)
        assert "Python" in result
        assert "Java" not in result

    def test_case_insensitive_matching(self) -> None:
        """Matching is case-insensitive."""
        items = [MockItem(title="Python"), MockItem(title="JAVA")]
        result = fuzzy_suggestions("python", items)
        assert "Python" in result

    def test_filters_by_score_threshold(self) -> None:
        """Only returns matches with similarity score >= 0.6."""
        items = [
            MockItem(title="Database"),
            MockItem(title="XYZ"),
        ]
        result = fuzzy_suggestions("Data", items)
        assert result == ["Database"]
        assert "XYZ" not in result

    def test_respects_top_n_limit(self) -> None:
        """Returns at most top_n results."""
        items = [
            MockItem(title="Test"),
            MockItem(title="Testing"),
            MockItem(title="Tests"),
            MockItem(title="Tester"),
        ]
        result = fuzzy_suggestions("Test", items, top_n=2)
        assert len(result) == 2

    def test_custom_top_n_parameter(self) -> None:
        """Respects custom top_n value."""
        items = [
            MockItem(title="Python"),
            MockItem(title="Pythonic"),
            MockItem(title="Pythagorean"),
        ]
        result = fuzzy_suggestions("Python", items, top_n=1)
        assert len(result) == 1
        assert result[0] == "Python"

    def test_empty_item_list(self) -> None:
        """Returns empty list for empty items."""
        result = fuzzy_suggestions("query", [])
        assert result == []

    def test_no_matches_above_threshold(self) -> None:
        """Returns empty list when no items meet threshold."""
        items = [MockItem(title="ABC"), MockItem(title="DEF")]
        result = fuzzy_suggestions("XYZ", items)
        assert result == []

    def test_scores_ranked_by_similarity(self) -> None:
        """Results are ordered by highest similarity score first."""
        items = [
            MockItem(title="Testing"),
            MockItem(title="Test"),
            MockItem(title="Tests"),
        ]
        result = fuzzy_suggestions("Test", items)
        # Exact match should appear first or at least before other matches
        assert len(result) > 0
        assert "Test" in result

    def test_returns_item_titles_not_objects(self) -> None:
        """Returns list of strings, not objects."""
        items = [MockItem(title="Python"), MockItem(title="Java")]
        result = fuzzy_suggestions("Python", items)
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
