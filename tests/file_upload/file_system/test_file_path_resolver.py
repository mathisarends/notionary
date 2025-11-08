from pathlib import Path

import pytest

from notionary.file_upload.file_system.models import FileInfo
from notionary.file_upload.file_system.resolver import FilePathResolver
from notionary.file_upload.validation.models import FileCategory


@pytest.fixture
def temp_base_dir(tmp_path: Path) -> Path:
    test_dir = tmp_path / "test_base"
    test_dir.mkdir()

    (test_dir / "document.pdf").write_text("pdf content")
    (test_dir / "image.png").write_bytes(b"fake png")
    (test_dir / "audio.mp3").write_bytes(b"fake mp3")
    (test_dir / "video.mp4").write_bytes(b"fake mp4")
    (test_dir / "unsupported.xyz").write_text("unsupported")

    sub_dir = test_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.txt").write_text("nested content")
    (sub_dir / "nested_image.jpg").write_bytes(b"fake jpg")

    return test_dir


@pytest.fixture
def file_path_resolver(temp_base_dir: Path) -> FilePathResolver:
    return FilePathResolver(base_path=temp_base_dir)


class TestFilePathResolverInitialization:
    def test_init_with_string_path(self, temp_base_dir: Path) -> None:
        file_path_resolver = FilePathResolver(base_path=str(temp_base_dir))

        assert file_path_resolver.base_path == temp_base_dir
        assert file_path_resolver.base_path.is_absolute()

    def test_init_with_path_object(self, temp_base_dir: Path) -> None:
        file_path_resolver = FilePathResolver(base_path=temp_base_dir)

        assert file_path_resolver.base_path == temp_base_dir
        assert file_path_resolver.base_path.is_absolute()

    def test_init_without_base_path(self) -> None:
        file_path_resolver = FilePathResolver()

        assert file_path_resolver.base_path == Path.cwd().resolve()


class TestFilePathResolverResolvePath:
    def test_resolve_relative_path(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        result = file_path_resolver.resolve_path("document.pdf")

        assert result == temp_base_dir / "document.pdf"
        assert result.is_absolute()

    def test_resolve_nested_relative_path(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        result = file_path_resolver.resolve_path("subdir/nested.txt")

        assert result == temp_base_dir / "subdir" / "nested.txt"
        assert result.is_absolute()

    def test_resolve_absolute_path_returns_as_is(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        absolute_path = temp_base_dir / "document.pdf"

        result = file_path_resolver.resolve_path(absolute_path)

        assert result == absolute_path
        assert result.is_absolute()

    def test_resolve_with_path_object(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        result = file_path_resolver.resolve_path(Path("document.pdf"))

        assert result == temp_base_dir / "document.pdf"


class TestFilePathResolverFileExists:
    def test_exists_for_existing_file(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        assert file_path_resolver.file_exists("document.pdf") is True

    def test_exists_for_non_existing_file(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        assert file_path_resolver.file_exists("nonexistent.txt") is False

    def test_exists_for_existing_directory_returns_false(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        assert file_path_resolver.file_exists("subdir") is False

    def test_exists_with_absolute_path(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        absolute_path = temp_base_dir / "document.pdf"

        assert file_path_resolver.file_exists(absolute_path) is True


class TestFilePathResolverGetFileInfo:
    def test_get_file_info_returns_correct_info(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        file_info = file_path_resolver._get_file_info("document.pdf")

        assert isinstance(file_info, FileInfo)
        assert file_info.name == "document.pdf"
        assert file_info.absolute_path == temp_base_dir / "document.pdf"
        assert file_info.size_bytes > 0

    def test_get_file_info_raises_for_non_existing_file(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        with pytest.raises(FileNotFoundError, match="File not found"):
            file_path_resolver._get_file_info("nonexistent.txt")

    def test_get_file_info_raises_for_directory(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        with pytest.raises(ValueError, match="Path is not a file"):
            file_path_resolver._get_file_info("subdir")


class TestFilePathResolverListFiles:
    def test_list_all_supported_files(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = file_path_resolver.list_files()

        file_names = [f.name for f in files]
        assert "document.pdf" in file_names
        assert "image.png" in file_names
        assert "audio.mp3" in file_names
        assert "video.mp4" in file_names
        assert "unsupported.xyz" not in file_names

    def test_list_files_recursive(self, file_path_resolver: FilePathResolver) -> None:
        files = file_path_resolver.list_files(recursive=True)

        file_names = [f.name for f in files]
        assert "nested.txt" in file_names
        assert "nested_image.jpg" in file_names
        assert len(files) >= 6

    def test_list_files_non_recursive_excludes_subdirs(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = file_path_resolver.list_files(recursive=False)

        file_names = [f.name for f in files]
        assert "nested.txt" not in file_names
        assert "nested_image.jpg" not in file_names

    def test_list_files_with_pattern(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = file_path_resolver.list_files(pattern="*.pdf")

        assert len(files) == 1
        assert files[0].name == "document.pdf"

    def test_list_files_include_unsupported(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = file_path_resolver.list_files(only_supported=False)

        file_names = [f.name for f in files]
        assert "unsupported.xyz" in file_names

    def test_list_files_filter_by_category_images(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = file_path_resolver.list_files(categories=[FileCategory.IMAGE])

        file_names = [f.name for f in files]
        assert "image.png" in file_names
        assert "document.pdf" not in file_names
        assert "audio.mp3" not in file_names

    def test_list_files_filter_by_multiple_categories(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = file_path_resolver.list_files(
            categories=[FileCategory.IMAGE, FileCategory.AUDIO]
        )

        file_names = [f.name for f in files]
        assert "image.png" in file_names
        assert "audio.mp3" in file_names
        assert "document.pdf" not in file_names

    def test_list_files_empty_directory(self, tmp_path: Path) -> None:
        empty_file_path_resolver = FilePathResolver(base_path=tmp_path)

        files = empty_file_path_resolver.list_files()

        assert files == []


class TestFilePathResolverIterFiles:
    def test_iter_files_yields_all_supported_files(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = list(file_path_resolver.iter_files())

        file_names = [f.name for f in files]
        assert "document.pdf" in file_names
        assert "image.png" in file_names
        assert "unsupported.xyz" not in file_names

    def test_iter_files_recursive(self, file_path_resolver: FilePathResolver) -> None:
        files = list(file_path_resolver.iter_files(recursive=True))

        file_names = [f.name for f in files]
        assert "nested.txt" in file_names
        assert "nested_image.jpg" in file_names

    def test_iter_files_with_category_filter(
        self, file_path_resolver: FilePathResolver
    ) -> None:
        files = list(file_path_resolver.iter_files(categories=[FileCategory.DOCUMENT]))

        file_names = [f.name for f in files]
        assert "document.pdf" in file_names
        assert "image.png" not in file_names

    def test_iter_files_is_lazy(self, file_path_resolver: FilePathResolver) -> None:
        iterator = file_path_resolver.iter_files()

        first_file = next(iterator)
        assert isinstance(first_file, FileInfo)


class TestFilePathResolverSupportedExtensions:
    def test_is_supported_file_for_supported_extension(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        pdf_path = temp_base_dir / "document.pdf"

        assert file_path_resolver._is_supported_file(pdf_path) is True

    def test_is_supported_file_for_unsupported_extension(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        xyz_path = temp_base_dir / "unsupported.xyz"

        assert file_path_resolver._is_supported_file(xyz_path) is False

    def test_is_supported_file_with_category_filter_matching(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        pdf_path = temp_base_dir / "document.pdf"

        assert (
            file_path_resolver._is_supported_file(
                pdf_path, categories=[FileCategory.DOCUMENT]
            )
            is True
        )

    def test_is_supported_file_with_category_filter_not_matching(
        self, file_path_resolver: FilePathResolver, temp_base_dir: Path
    ) -> None:
        pdf_path = temp_base_dir / "document.pdf"

        assert (
            file_path_resolver._is_supported_file(
                pdf_path, categories=[FileCategory.IMAGE]
            )
            is False
        )


@pytest.mark.parametrize(
    "filename,expected_exists",
    [
        ("document.pdf", True),
        ("image.png", True),
        ("audio.mp3", True),
        ("nonexistent.txt", False),
        ("subdir/nested.txt", True),
    ],
)
def test_file_exists_parametrized(
    file_path_resolver: FilePathResolver, filename: str, expected_exists: bool
) -> None:
    result = file_path_resolver.file_exists(filename)

    assert result is expected_exists


@pytest.mark.parametrize(
    "pattern,expected_count",
    [
        ("*.pdf", 1),
        ("*.png", 1),
        ("*.mp3", 1),
        ("*.txt", 0),
    ],
)
def test_list_files_with_patterns(
    file_path_resolver: FilePathResolver, pattern: str, expected_count: int
) -> None:
    files = file_path_resolver.list_files(pattern=pattern)

    assert len(files) == expected_count
