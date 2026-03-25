"""
Backward-compatible re-exports of UUID utilities.

The canonical location for these helpers is notionary.shared.entity.metadata.
"""

from notionary.shared.entity.metadata import extract_uuid, is_valid_uuid

__all__ = ["extract_uuid", "is_valid_uuid"]
