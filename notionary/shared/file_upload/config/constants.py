"""
Fixed API limits and recommendations from Notion.
These values should not be changed, as they are specified by the API.

Source: https://developers.notion.com/reference/file-uploads
"""

_MB = 1024 * 1024

NOTION_SINGLE_PART_MAX_SIZE: int = 20 * _MB
NOTION_MAX_FILENAME_BYTES: int = 900

NOTION_MULTI_PART_CHUNK_SIZE_MIN: int = 5 * _MB
NOTION_MULTI_PART_CHUNK_SIZE_MAX: int = 20 * _MB

NOTION_RECOMMENDED_CHUNK_SIZE: int = 10 * _MB
