from __future__ import annotations

from abc import ABC, abstractmethod


class MarkdownNode(ABC):
    """
    Abstract base class for all Markdown block elements.
    Enforces implementation of to_markdown().
    """

    @abstractmethod
    def to_markdown(self) -> str:
        """
        Returns the Markdown representation of the block.
        Must be implemented by subclasses.
        """
        pass

    @classmethod
    @abstractmethod
    def from_params(cls, params) -> MarkdownNode:
        """
        Creates an instance from a params object.
        Must be implemented by subclasses.
        """
        pass

    def __str__(self):
        return self.to_markdown()
