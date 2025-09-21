from abc import ABC, abstractmethod

from pydantic import BaseModel


class MarkdownNode(BaseModel, ABC):
    """
    Enhanced base class for all Markdown nodes with Pydantic integration.

    This class serves dual purposes:
    1. Runtime representation for markdown generation
    2. Serializable model for structured output (LLM/API)

    The 'type' field acts as a discriminator for Union types and processing.
    """

    @abstractmethod
    def to_markdown(self) -> str:
        """
        Returns the Markdown representation of the block.
        Must be implemented by subclasses.
        """
        pass

    def __str__(self):
        return self.to_markdown()
