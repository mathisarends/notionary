from collections.abc import AsyncGenerator
from pathlib import Path

import aiofiles

from notionary.file_upload.config.config import FileUploadConfig


class FileContentReader:
    def __init__(self, config: FileUploadConfig | None = None):
        config = config or FileUploadConfig()
        self._chunk_size = config.multi_part_chunk_size

    async def read_full_file(self, file_path: Path) -> bytes:
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def read_file_chunks(self, file_path: Path) -> AsyncGenerator[bytes]:
        async with aiofiles.open(file_path, "rb") as file:
            while True:
                chunk = await file.read(self._chunk_size)
                if not chunk:
                    break
                yield chunk

    async def bytes_to_chunks(self, file_content: bytes) -> AsyncGenerator[bytes]:
        for i in range(0, len(file_content), self._chunk_size):
            yield file_content[i : i + self._chunk_size]
