"""
MASSIVELY SIMPLIFIED processor that works directly with existing MarkdownNode classes.
NO MORE ProcessorModel -> MarkdownNode mapping needed!
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.markdown.markdown_builder import MarkdownBuilder

from notionary.markdown.markdown_document_model import (
    MarkdownBlock,
    MarkdownDocumentModel,
)


class MarkdownModelProcessor:
    """
    SIMPLIFIED processor - nodes ARE the models now!
    
    Benefits:
    - No mapping between ProcessorModel and MarkdownNode needed
    - Existing MarkdownNode classes are reused (no redundancy)
    - Direct processing - nodes can be added straight to builder
    - Much less code!
    """

    def __init__(self, builder: MarkdownBuilder):
        """Initialize processor with a MarkdownBuilder instance."""
        self.builder = builder

    def process(self, input: MarkdownDocumentModel | list[MarkdownBlock]) -> None:
        """
        Process nodes directly - NO CONVERSION NEEDED!
        
        Args:
            input: The MarkdownDocumentModel or list of MarkdownBlock instances to process
        """
        if isinstance(input, MarkdownDocumentModel):
            blocks = input.blocks
        else:
            blocks = input

        for block in blocks:
            # DIRECT PROCESSING! 
            # The block IS already a MarkdownNode - just add it!
            self.builder.children.append(block)
