import pytest


class MockNameIdResolver:
    async def resolve_name_to_id(self, name: str | None) -> str | None:
        return None

    async def resolve_id_to_name(self, id: str | None) -> str | None:
        return None


@pytest.fixture
def mock_page_resolver() -> MockNameIdResolver:
    return MockNameIdResolver()


@pytest.fixture
def mock_database_resolver() -> MockNameIdResolver:
    return MockNameIdResolver()


@pytest.fixture
def mock_data_source_resolver() -> MockNameIdResolver:
    return MockNameIdResolver()


@pytest.fixture
def mock_person_resolver() -> MockNameIdResolver:
    return MockNameIdResolver()
