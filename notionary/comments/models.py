from dataclasses import dataclass


@dataclass
class Comment:
    author_name: str
    content: str
