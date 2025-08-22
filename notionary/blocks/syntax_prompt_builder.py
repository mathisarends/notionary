from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from notionary.blocks.registry.block_registry import BlockRegistry


@dataclass
class BlockElementMarkdownInformation:
    """Metadata describing how a Notion block maps to Markdown syntax."""

    block_type: str
    description: str
    syntax_examples: list[str]
    usage_guidelines: str


class SyntaxPromptBuilder:
    """
    Builds a comprehensive markdown syntax reference from a block registry.
    Iterates over all registered elements and collects their system prompt information.
    """

    def __init__(self, block_registry: BlockRegistry):
        self.block_registry = block_registry

    def build_markdown_reference(self) -> str:
        """
        Build a complete markdown syntax reference string.
        """
        sections = [
            self._build_header(),
            *self._build_element_sections(),
        ]

        return "\n\n".join(sections)

    def build_concise_reference(self) -> str:
        """
        Build a more concise reference suitable for system prompts.
        """
        lines = ["# Notionary Markdown Syntax"]

        for element_class in self.block_registry.get_elements():
            info: Optional[BlockElementMarkdownInformation] = (
                element_class.get_system_prompt_information()
            )
            if info and info.syntax_examples:
                # Just show the first example for conciseness
                example = info.syntax_examples[0]
                lines.append(f"- {info.block_type}: `{example}`")

        return "\n".join(lines)

    def get_blocks_with_information(self) -> list[str]:
        """Get list of block names that provide system prompt information."""
        blocks = []

        for element_class in self.block_registry.get_elements():
            info: Optional[BlockElementMarkdownInformation] = (
                element_class.get_system_prompt_information()
            )
            if info:
                blocks.append(info.block_type)

        return blocks

    def _build_header(self) -> str:
        """Build the header section of the reference."""
        return dedent(
            """
            # Notionary Markdown Syntax Reference

            This comprehensive reference documents all supported markdown syntax for converting between Markdown and Notion blocks.
            
            Each block type includes:
            - **Description:** What the block does
            - **When to use:** Guidelines for appropriate usage
            - **Syntax:** Complete syntax examples with variations
        """
        ).strip()

    def _build_element_sections(self) -> list[str]:
        """Build sections for all registered elements."""
        sections = []

        for element_class in self.block_registry.get_elements():
            info = element_class.get_system_prompt_information()
            if info:
                sections.append(self._build_element_section(info))

        return sections

    def _build_element_section(self, info: BlockElementMarkdownInformation) -> str:
        """Build a well-structured section for a single block element."""
        section_parts = [
            f"## {info.block_type}",
            "",
            f"**Description:** {info.description}",
            "",
        ]

        if info.usage_guidelines:
            section_parts.extend(["**When to use:**", info.usage_guidelines, ""])

        if info.syntax_examples:
            section_parts.extend(
                [
                    "**Syntax:**",
                    "",
                    *self._format_syntax_examples(info.syntax_examples),
                    "",
                ]
            )

        return "\n".join(section_parts).rstrip()

    def _format_syntax_examples(self, examples: list[str]) -> list[str]:
        """Format syntax examples with proper markdown and clear structure."""
        formatted = []

        for i, example in enumerate(examples, 1):
            if len(examples) > 1:
                formatted.append(f"**Example {i}:**")

            if "\n" in example:
                # Multi-line example - use code block
                formatted.extend(["```", example, "```", ""])
            else:
                # Single line - use inline code with description
                formatted.extend([f"`{example}`", ""])

        return formatted
