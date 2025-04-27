from typing import Type, List
from notionary.elements.notion_block_element import NotionBlockElement


class MarkdownSyntaxPromptBuilder:
    """
    Generator for LLM system prompts that describe Notion-Markdown syntax.

    This class extracts information about supported Markdown patterns
    and formats them optimally for LLMs.
    """

    SYSTEM_PROMPT_TEMPLATE = """You are a knowledgeable assistant that helps users create content for Notion pages.
Notion supports standard Markdown with some special extensions for creating rich content.

{element_docs}

CRITICAL USAGE GUIDELINES:

1. Do NOT start content with a level 1 heading (# Heading). In Notion, the page title is already displayed in the metadata, so starting with an H1 heading is redundant. Begin with H2 (## Heading) or lower for section headings.

2. BACKTICK HANDLING - EXTREMELY IMPORTANT:
   ❌ NEVER wrap entire content or responses in triple backticks (```).
   ❌ DO NOT use triple backticks (```) for anything except CODE BLOCKS or DIAGRAMS.
   ❌ DO NOT use triple backticks to mark or highlight regular text or examples.
   ✅ USE triple backticks ONLY for actual programming code, pseudocode, or specialized notation.
   ✅ When showing Markdown syntax examples, use inline code formatting with single backticks.

3. Use inline formatting (bold, italic, etc.) across all content to enhance readability.
   Proper typography is essential for creating scannable, well-structured documents.

4. Notion's extensions to Markdown provide richer formatting options than standard Markdown
   while maintaining the familiar Markdown syntax for basic elements.

5. Always structure content with clear headings, lists, and paragraphs to create visually appealing
   and well-organized documents.
"""

    @staticmethod
    def generate_element_doc(element_class: Type[NotionBlockElement]) -> str:
        """
        Generates documentation for a specific NotionBlockElement in a compact format.
        Uses the element's get_llm_prompt_content method if available.
        """
        class_name = element_class.__name__
        element_name = class_name.replace("Element", "")

        # Check if the class has the get_llm_prompt_content method
        if not hasattr(element_class, "get_llm_prompt_content") or not callable(
            getattr(element_class, "get_llm_prompt_content")
        ):
            return f"## {element_name}"

        # Get the element content
        content = element_class.get_llm_prompt_content()

        # Format the element documentation in a compact way
        doc_parts = [
            f"## {element_name}",
            f"{content['description']}",
            f"**Syntax:** {content['syntax']}",
            f"**Example:** {content['examples'][0]}" if content["examples"] else "",
            f"**When to use:** {content['when_to_use']}",
        ]

        # Filter out any empty parts and join with newlines
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
