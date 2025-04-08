from typing import Optional, TypedDict


class PageResult(TypedDict, total=False):
    """Type definition for page operation results."""

    success: bool
    page_id: str
    url: Optional[str]
    message: Optional[str]
