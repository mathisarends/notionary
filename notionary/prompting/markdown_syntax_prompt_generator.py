from textwrap import dedent
from typing import Type, List
from notionary.elements.notion_block_element import NotionBlockElement


class MarkdownSyntaxPromptGenerator:
    """
    Generator for LLM system prompts that describe Notion-Markdown syntax.

    This class extracts information about supported Markdown patterns
    and formats them optimally for LLMs.
    """

    SYSTEM_PROMPT_TEMPLATE = dedent(
        """
    You are a knowledgeable assistant that helps users create content for Notion pages.
    Notion supports standard Markdown with some special extensions for creating rich content.

    # Understanding Notion Blocks

    Notion documents are composed of individual blocks. Each block has a specific type (paragraph, heading, list item, etc.) and format.
    The Markdown syntax you use directly maps to these Notion blocks.

    {element_docs}

    CRITICAL USAGE GUIDELINES:

    1. Do NOT start content with a level 1 heading (# Heading). In Notion, the page title is already displayed in the metadata, so starting with an H1 heading is redundant. Begin with H2 (## Heading) or lower for section headings.

    2. INLINE FORMATTING - VERY IMPORTANT:
    ✅ You can use inline formatting within almost any block type.
    ✅ Combine **bold**, _italic_, `code`, and other formatting as needed.
    ✅ Format text to create visual hierarchy and emphasize important points.
    ❌ DO NOT overuse formatting - be strategic with formatting for best readability.

    3. BACKTICK HANDLING - EXTREMELY IMPORTANT:
    ❌ NEVER wrap entire content or responses in triple backticks (```).
    ❌ DO NOT use triple backticks (```) for anything except CODE BLOCKS or DIAGRAMS.
    ❌ DO NOT use triple backticks to mark or highlight regular text or examples.
    ✅ USE triple backticks ONLY for actual programming code, pseudocode, or specialized notation.
    ✅ For inline code, use single backticks (`code`).
    ✅ When showing Markdown syntax examples, use inline code formatting with single backticks.

    4. BLOCK SEPARATION - IMPORTANT:
    ✅ Use empty lines between different blocks to ensure proper rendering in Notion.
    ✅ For major logical sections, use the spacer element (see documentation below).
    ⚠️ While headings can sometimes work without an empty line before the following paragraph, including empty lines between all block types ensures consistent rendering.

    5. CONTENT FORMATTING - CRITICAL:
    ❌ DO NOT include introductory phrases like "I understand that..." or "Here's the content...".
    ✅ Provide ONLY the requested content directly without any prefacing text or meta-commentary.
    ✅ Generate just the content itself, formatted according to these guidelines."""
    )

    @staticmethod
    def generate_element_doc(element_class: Type[NotionBlockElement]) -> str:
        """
        Generates documentation for a specific NotionBlockElement in a compact format.
        Uses the element's get_llm_prompt_content method if available.
        """
        class_name = element_class.__name__
        element_name = class_name.replace("Element", "")

        content = element_class.get_llm_prompt_content()

        doc_parts = [
            f"## {element_name}",
            f"{content.description}",
            f"**Syntax:** {content.syntax}",
        ]

        if content.examples:
            doc_parts.append("**Examples:**")
            for example in content.examples:
                doc_parts.append(example)

        doc_parts.append(f"**When to use:** {content.when_to_use}")

        if content.avoid:
            doc_parts.append(f"**Avoid:** {content.avoid}")

        return "\n".join([part for part in doc_parts if part])

    @classmethod
    def generate_element_docs(
        cls, element_classes: List[Type[NotionBlockElement]]
    ) -> str:
        """
        Generates complete documentation for all provided element classes.
        """
        docs = [
            "# Markdown Syntax for Notion Blocks",
            "The following Markdown patterns are supported for creating Notion blocks:",
        ]

        # Generate docs for each element
        for element in element_classes:
            docs.append("\n" + cls.generate_element_doc(element))

        return "\n".join(docs)

    @classmethod
    def generate_system_prompt(
        cls,
        element_classes: List[Type[NotionBlockElement]],
    ) -> str:
        """
        Generates a complete system prompt for LLMs.
        """
        element_docs = cls.generate_element_docs(element_classes)
        return cls.SYSTEM_PROMPT_TEMPLATE.format(element_docs=element_docs)
