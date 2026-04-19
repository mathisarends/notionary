from notionary.workspace.exceptions import ResourceNotFound


class TestResourceNotFound:
    def test_message_with_suggestions(self) -> None:
        exc = ResourceNotFound("my query", ["Option A", "Option B"])

        assert "my query" in str(exc)
        assert "Option A" in str(exc)
        assert "Option B" in str(exc)

    def test_message_without_suggestions(self) -> None:
        exc = ResourceNotFound("my query")

        assert "my query" in str(exc)
        assert "no results" in str(exc).lower()

    def test_is_entity_not_found(self) -> None:
        from notionary.shared.exceptions import EntityNotFound

        exc = ResourceNotFound("test")
        assert isinstance(exc, EntityNotFound)

    def test_available_titles_stored(self) -> None:
        exc = ResourceNotFound("q", ["A", "B"])

        assert exc.available_titles == ["A", "B"]

    def test_none_titles_defaults_to_empty_list(self) -> None:
        exc = ResourceNotFound("q", None)

        assert exc.available_titles == []
