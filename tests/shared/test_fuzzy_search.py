from notionary.shared.search.fuzzy import fuzzy_suggestions


class _Item:
    def __init__(self, title: str) -> None:
        self.title = title


class TestFuzzySuggestions:
    def test_exact_match_returned(self) -> None:
        items = [_Item("Project Alpha"), _Item("Project Beta")]
        results = fuzzy_suggestions("Project Alpha", items)

        assert "Project Alpha" in results

    def test_partial_match_returned(self) -> None:
        items = [_Item("Budget Planning"), _Item("Budget Review"), _Item("Marketing")]
        results = fuzzy_suggestions("Budget", items)

        assert len(results) >= 1
        assert all("Budget" in r for r in results)

    def test_low_similarity_excluded(self) -> None:
        items = [_Item("Completely Unrelated")]
        results = fuzzy_suggestions("zzz", items)

        assert results == []

    def test_empty_items_returns_empty(self) -> None:
        results = fuzzy_suggestions("anything", [])

        assert results == []

    def test_top_n_limit_respected(self) -> None:
        items = [_Item(f"Project {i}") for i in range(20)]
        results = fuzzy_suggestions("Project", items, top_n=3)

        assert len(results) <= 3

    def test_case_insensitive_matching(self) -> None:
        items = [_Item("HELLO WORLD")]
        results = fuzzy_suggestions("hello world", items)

        assert "HELLO WORLD" in results
