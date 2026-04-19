from pydantic import BaseModel


class Comment(BaseModel):
    """A resolved comment with author name and markdown content."""

    author_name: str
    content: str
