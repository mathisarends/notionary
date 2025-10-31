from pathlib import Path
from unittest.mock import patch

import pytest

from notionary.utils import AbsoluteFilePathResolver


@pytest.fixture
def resolver() -> AbsoluteFilePathResolver:
    return AbsoluteFilePathResolver()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.txt").write_text("content3")
    return tmp_path


@pytest.fixture
def resolver_with_base_path(temp_dir: Path) -> AbsoluteFilePathResolver:
    return AbsoluteFilePathResolver(base_path=temp_dir)


# Base Path Tests
def test_init_without_base_path(resolver: AbsoluteFilePathResolver) -> None:
    assert resolver.base_path is None


def test_init_with_valid_base_path(temp_dir: Path) -> None:
    resolver = AbsoluteFilePathResolver(base_path=temp_dir)
    assert resolver.base_path == temp_dir.resolve()


def test_set_valid_base_path(
    resolver: AbsoluteFilePathResolver, temp_dir: Path
) -> None:
    resolver.base_path = temp_dir
    assert resolver.base_path == temp_dir.resolve()


def test_unset_base_path(resolver_with_base_path: AbsoluteFilePathResolver) -> None:
    resolver_with_base_path.base_path = None
    assert resolver_with_base_path.base_path is None


def test_set_nonexistent_path_raises_error(resolver: AbsoluteFilePathResolver) -> None:
    with pytest.raises(ValueError, match="Path does not exist"):
        resolver.base_path = Path("/nonexistent/path")


def test_set_file_as_base_path_raises_error(
    resolver: AbsoluteFilePathResolver, temp_dir: Path
) -> None:
    with pytest.raises(ValueError, match="Path is not a directory"):
        resolver.base_path = temp_dir / "file1.txt"


def test_base_path_is_always_absolute(
    resolver: AbsoluteFilePathResolver, temp_dir: Path
) -> None:
    resolver.base_path = temp_dir
    assert resolver.base_path.is_absolute()


# Resolve to Absolute Tests
def test_resolve_absolute_path_without_base_path(
    resolver: AbsoluteFilePathResolver,
) -> None:
    absolute_path = Path("/some/absolute/path/file.txt")
    result = resolver.resolve_to_absolute(absolute_path)
    assert result == absolute_path


def test_resolve_relative_path_without_base_path(
    resolver: AbsoluteFilePathResolver,
) -> None:
    relative_path = Path("relative/file.txt")
    result = resolver.resolve_to_absolute(relative_path)

    assert result == (Path.cwd() / relative_path).resolve()
    assert result.is_absolute()


def test_resolve_relative_path_with_base_path(
    resolver_with_base_path: AbsoluteFilePathResolver, temp_dir: Path
) -> None:
    result = resolver_with_base_path.resolve_to_absolute("subdir/file.txt")

    assert result == (temp_dir / "subdir/file.txt").resolve()
    assert result.is_absolute()


def test_resolve_absolute_path_ignores_base_path(
    resolver_with_base_path: AbsoluteFilePathResolver,
) -> None:
    absolute_path = Path("/other/absolute/path/file.txt")
    result = resolver_with_base_path.resolve_to_absolute(absolute_path)
    assert result == absolute_path


def test_resolve_accepts_string_paths(
    resolver_with_base_path: AbsoluteFilePathResolver, temp_dir: Path
) -> None:
    result = resolver_with_base_path.resolve_to_absolute("file.txt")
    assert result == (temp_dir / "file.txt").resolve()


@pytest.mark.parametrize(
    "relative_path",
    ["file.txt", "subdir/file.txt", "./file.txt", "subdir/../file.txt"],
)
def test_resolve_various_relative_formats(
    resolver_with_base_path: AbsoluteFilePathResolver,
    temp_dir: Path,
    relative_path: str,
) -> None:
    result = resolver_with_base_path.resolve_to_absolute(relative_path)

    assert result.is_absolute()
    assert str(temp_dir) in str(result)


# Directory Contents Tests
def test_get_directory_contents_returns_files(
    resolver_with_base_path: AbsoluteFilePathResolver,
) -> None:
    contents = resolver_with_base_path._get_directory_contents()

    assert len(contents) == 3
    names = {p.name for p in contents}
    assert names == {"file1.txt", "file2.txt", "subdir"}


def test_get_directory_contents_without_base_path_returns_empty(
    resolver: AbsoluteFilePathResolver,
) -> None:
    assert resolver._get_directory_contents() == []


def test_get_directory_contents_handles_errors(
    resolver_with_base_path: AbsoluteFilePathResolver,
) -> None:
    with patch.object(Path, "iterdir", side_effect=PermissionError()):
        assert resolver_with_base_path._get_directory_contents() == []


# Logging Tests
def test_set_base_path_logs_info(
    resolver: AbsoluteFilePathResolver, temp_dir: Path
) -> None:
    with patch.object(resolver, "logger") as mock_logger:
        resolver.base_path = temp_dir
        mock_logger.info.assert_any_call(f"Base path set: {temp_dir.resolve()}")


def test_unset_base_path_logs_info(
    resolver_with_base_path: AbsoluteFilePathResolver,
) -> None:
    with patch.object(resolver_with_base_path, "logger") as mock_logger:
        resolver_with_base_path.base_path = None
        mock_logger.info.assert_called_with("Base path unset.")


def test_resolve_logs_debug_messages(
    resolver_with_base_path: AbsoluteFilePathResolver,
) -> None:
    with patch.object(resolver_with_base_path, "logger") as mock_logger:
        resolver_with_base_path.resolve_to_absolute("file.txt")
        assert mock_logger.debug.called


def test_invalid_path_logs_error(resolver: AbsoluteFilePathResolver) -> None:
    with patch.object(resolver, "logger") as mock_logger:
        with pytest.raises(ValueError):
            resolver.base_path = Path("/nonexistent")
        mock_logger.error.assert_called_once()


# Integration Test
def test_full_workflow(temp_dir: Path) -> None:
    resolver = AbsoluteFilePathResolver()
    resolver.base_path = temp_dir

    file_path = resolver.resolve_to_absolute("file1.txt")
    assert file_path == temp_dir / "file1.txt"
    assert file_path.exists()

    nested_path = resolver.resolve_to_absolute("subdir/file3.txt")
    assert nested_path == temp_dir / "subdir/file3.txt"

    contents = resolver._get_directory_contents()
    assert len(contents) > 0
