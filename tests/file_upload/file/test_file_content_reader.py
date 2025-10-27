from pathlib import Path

import pytest

from notionary.file_upload.config.config import FileUploadConfig
from notionary.file_upload.file.reader import FileContentReader


@pytest.fixture
def file_reader():
    config = FileUploadConfig.model_construct(multi_part_chunk_size=10)
    return FileContentReader(config=config)


@pytest.fixture
def test_file(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    content = b"Hello World! This is a test file with some content."
    file_path.write_bytes(content)
    return file_path, content


class TestFileContentReader:
    @pytest.mark.asyncio
    async def test_read_full_file(
        self, file_reader: FileContentReader, test_file: tuple[Path, bytes]
    ):
        file_path, expected_content = test_file

        content = await file_reader.read_full_file(file_path)

        assert content == expected_content

    @pytest.mark.asyncio
    async def test_read_file_chunks(
        self, file_reader: FileContentReader, test_file: tuple[Path, bytes]
    ):
        file_path, expected_content = test_file
        chunks = []

        async for chunk in file_reader.read_file_chunks(file_path):
            chunks.append(chunk)

        reconstructed_content = b"".join(chunks)
        assert reconstructed_content == expected_content
        assert all(len(chunk) <= file_reader._chunk_size for chunk in chunks)

    @pytest.mark.asyncio
    async def test_read_file_chunks_respects_chunk_size(
        self, file_reader: FileContentReader, test_file: tuple[Path, bytes]
    ):
        file_path, _ = test_file
        chunks = []

        async for chunk in file_reader.read_file_chunks(file_path):
            chunks.append(chunk)

        for chunk in chunks[:-1]:
            assert len(chunk) == 10
        assert len(chunks[-1]) <= 10

    @pytest.mark.asyncio
    async def test_bytes_to_chunks(self, file_reader: FileContentReader):
        test_bytes = b"A" * 25
        chunks = []

        async for chunk in file_reader.bytes_to_chunks(test_bytes):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0] == b"A" * 10
        assert chunks[1] == b"A" * 10
        assert chunks[2] == b"A" * 5

    @pytest.mark.asyncio
    async def test_bytes_to_chunks_exact_chunk_size(
        self, file_reader: FileContentReader
    ):
        test_bytes = b"B" * 20
        chunks = []

        async for chunk in file_reader.bytes_to_chunks(test_bytes):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert all(len(chunk) == 10 for chunk in chunks)

    @pytest.mark.asyncio
    async def test_bytes_to_chunks_empty(self, file_reader: FileContentReader):
        test_bytes = b""
        chunks = []

        async for chunk in file_reader.bytes_to_chunks(test_bytes):
            chunks.append(chunk)

        assert len(chunks) == 0

    @pytest.mark.asyncio
    async def test_read_full_file_empty_file(
        self, file_reader: FileContentReader, tmp_path: Path
    ):
        empty_file = tmp_path / "empty.txt"
        empty_file.write_bytes(b"")

        content = await file_reader.read_full_file(empty_file)

        assert content == b""

    @pytest.mark.asyncio
    async def test_default_config(self, tmp_path: Path):
        reader = FileContentReader()
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"test content")

        content = await reader.read_full_file(test_file)

        assert content == b"test content"

    @pytest.mark.asyncio
    async def test_bytes_to_chunks_single_byte(self, file_reader: FileContentReader):
        test_bytes = b"X"
        chunks = []

        async for chunk in file_reader.bytes_to_chunks(test_bytes):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0] == b"X"
