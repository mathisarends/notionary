# File path resolver utility

`FilePathResolver` is a small convenience class that helps you work with absolute and relative file paths when preparing uploads. It resolves paths against a base directory, lists files (optionally filtered by category and pattern), and yields structured `FileInfo` objects.

## Basic usage

```python
from pathlib import Path
from notionary import FilePathResolver

base = Path.cwd() / "assets"
file_path_resolver = FilePathResolver(base_path=base)

# Resolve a path (relative or absolute)
abs_path = file_path_resolver.resolve_path("images/logo.png")

# Check existence
if file_path_resolver.file_exists("images/logo.png"):
	print("exists!")
```

## List and iterate files

```python
from notionary.file_upload.validation.models import FileCategory

# Non‑recursive, only supported extensions
files = file_path_resolver.list_files()

# Recursive with category filtering (e.g., only images)
images = file_path_resolver.list_files(recursive=True, categories=[FileCategory.IMAGE])

# Lazy iteration
for info in file_path_resolver.iter_files(pattern="*.png", recursive=True):
	print(info.name, info.absolute_path)
```

## When to use

- Normalize user‑provided paths before uploading
- Batch select files from a directory (e.g., all images under `assets/`)
- Keep a clean separation between path discovery and the actual upload step
