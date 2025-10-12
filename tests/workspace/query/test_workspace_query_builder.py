import pytest

from notionary.workspace.query.builder import WorkspaceQueryConfigBuilder
from notionary.workspace.query.models import (
    SortDirection,
    SortTimestamp,
    WorkspaceQueryConfig,
    WorkspaceQueryObjectType,
)


@pytest.fixture
def builder() -> WorkspaceQueryConfigBuilder:
    return WorkspaceQueryConfigBuilder()


def test_builder_creates_default_config(builder: WorkspaceQueryConfigBuilder):
    config = builder.build()

    assert isinstance(config, WorkspaceQueryConfig)
    assert config.query is None
    assert config.object_type is None


def test_with_query_sets_query_string(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_query("test query").build()

    assert config.query == "test query"


def test_with_pages_only_sets_object_type(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_pages_only().build()

    assert config.object_type == WorkspaceQueryObjectType.PAGE


def test_with_data_sources_only_sets_object_type(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_data_sources_only().build()

    assert config.object_type == WorkspaceQueryObjectType.DATA_SOURCE


def test_with_sort_ascending(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_sort_ascending().build()

    assert config.sort_direction == SortDirection.ASCENDING


def test_with_sort_descending(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_sort_descending().build()

    assert config.sort_direction == SortDirection.DESCENDING


def test_with_sort_by_created_time(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_sort_by_created_time().build()

    assert config.sort_timestamp == SortTimestamp.CREATED_TIME


def test_with_sort_by_last_edited(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_sort_by_last_edited().build()

    assert config.sort_timestamp == SortTimestamp.LAST_EDITED_TIME


def test_with_page_size_sets_size(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_page_size(50).build()

    assert config.page_size == 50


def test_with_page_size_caps_at_100(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_page_size(150).build()

    assert config.page_size == 100


def test_with_start_cursor_sets_cursor(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_start_cursor("cursor-123").build()

    assert config.start_cursor == "cursor-123"


def test_without_cursor_clears_cursor(builder: WorkspaceQueryConfigBuilder):
    config = builder.with_start_cursor("cursor-123").without_cursor().build()

    assert config.start_cursor is None


def test_builder_chaining_works(builder: WorkspaceQueryConfigBuilder):
    config = (
        builder.with_query("project")
        .with_pages_only()
        .with_sort_descending()
        .with_sort_by_last_edited()
        .with_page_size(75)
        .build()
    )

    assert config.query == "project"
    assert config.object_type == WorkspaceQueryObjectType.PAGE
    assert config.sort_direction == SortDirection.DESCENDING
    assert config.sort_timestamp == SortTimestamp.LAST_EDITED_TIME
    assert config.page_size == 75


def test_builder_with_existing_config():
    existing_config = WorkspaceQueryConfig()
    existing_config.query = "existing"

    builder = WorkspaceQueryConfigBuilder(config=existing_config)
    config = builder.with_pages_only().build()

    assert config.query == "existing"
    assert config.object_type == WorkspaceQueryObjectType.PAGE


def test_multiple_builds_return_same_config(builder: WorkspaceQueryConfigBuilder):
    """Builder returns the same config instance on multiple builds"""
    config1 = builder.with_query("test").build()
    config2 = builder.build()

    assert config1 is config2
