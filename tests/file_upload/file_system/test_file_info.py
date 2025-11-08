from pathlib import Path

import pytest

from notionary.file_upload.file_system.models import FileInfo


class TestFileInfoSizeCalculations:
    def test_size_kb_calculation(self) -> None:
        file_info = FileInfo(
            name="test.txt",
            path=Path("test.txt"),
            size_bytes=2048,
            absolute_path=Path("/tmp/test.txt"),
        )

        assert file_info.size_kb == 2.0

    def test_size_mb_calculation(self) -> None:
        file_info = FileInfo(
            name="test.txt",
            path=Path("test.txt"),
            size_bytes=1048576,
            absolute_path=Path("/tmp/test.txt"),
        )

        assert file_info.size_mb == 1.0

    def test_size_kb_with_fractional_result(self) -> None:
        file_info = FileInfo(
            name="test.txt",
            path=Path("test.txt"),
            size_bytes=1536,
            absolute_path=Path("/tmp/test.txt"),
        )

        assert file_info.size_kb == 1.5


@pytest.mark.parametrize(
    "size_bytes,expected_kb,expected_mb",
    [
        (1024, 1.0, 0.0009765625),
        (1048576, 1024.0, 1.0),
        (5242880, 5120.0, 5.0),
        (0, 0.0, 0.0),
    ],
)
def test_file_info_size_conversions(
    size_bytes: int, expected_kb: float, expected_mb: float
) -> None:
    file_info = FileInfo(
        name="test.txt",
        path=Path("test.txt"),
        size_bytes=size_bytes,
        absolute_path=Path("/tmp/test.txt"),
    )

    assert file_info.size_kb == pytest.approx(expected_kb)
    assert file_info.size_mb == pytest.approx(expected_mb)
