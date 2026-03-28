from dataclasses import dataclass


@dataclass
class Comment:
    """A resolved comment with author name and markdown content."""

    author_name: str
    content: str
