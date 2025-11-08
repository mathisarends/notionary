from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileInfo:
    name: str
    path: Path
    size_bytes: int
    absolute_path: Path

    @property
    def size_kb(self) -> float:
        return self.size_bytes / 1024

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)
