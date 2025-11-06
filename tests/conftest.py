import pytest


@pytest.fixture(autouse=True)
def mock_notion_env_vars(monkeypatch):
    monkeypatch.setenv("NOTION_SECRET", "dummy_secret_for_pytest")
