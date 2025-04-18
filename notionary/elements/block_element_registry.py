from typing import Dict, Any, Optional, List, Type

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.text_inline_formatter import TextInlineFormatter


class BlockElementRegistry:
    """Registry of elements that can convert between Markdown and Notion."""

    def __init__(self, elements=None):
        """
        Initialize a new registry instance.

        Args:
            elements: Optional list of NotionBlockElement classes to register at creation
        """
        self._elements = []

        # Register initial elements if provided
        if elements:
            for element in elements:
                self.register(element)

    def register(self, element_class: Type[NotionBlockElement]):
        """Register an element class."""
        self._elements.append(element_class)
        return self

    def deregister(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Deregister an element class.

        Args:
            element_class: The element class to remove from the registry

        Returns:
            bool: True if the element was removed, False if it wasn't in the registry
        """
        if element_class in self._elements:
            self._elements.remove(element_class)
            return True
        return False

    def clear(self):
        """Clear the registry completely."""
        self._elements.clear()
        return self

    def find_markdown_handler(self, text: str) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given markdown text."""
        for element in self._elements:
            if element.match_markdown(text):
                return element
        return None

    def find_notion_handler(
        self, block: Dict[str, Any]
    ) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given Notion block."""
        for element in self._elements:
            if element.match_notion(block):
                return element
        return None

    def markdown_to_notion(self, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block using registered elements."""
        handler = self.find_markdown_handler(text)
        if handler:
            return handler.markdown_to_notion(text)
        return None

    def notion_to_markdown(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown using registered elements."""
        handler = self.find_notion_handler(block)
        if handler:
            return handler.notion_to_markdown(block)
        return None

    def get_multiline_elements(self) -> List[Type[NotionBlockElement]]:
        """Get all registered multiline elements."""
        return [element for element in self._elements if element.is_multiline()]

    def get_elements(self) -> List[Type[NotionBlockElement]]:
        """Get all registered elements."""
        return self._elements.copy()

    def generate_llm_prompt(self) -> str:
        """
        Generates an LLM system prompt that describes the Markdown syntax of all registered elements.

        TextInlineFormatter is automatically added if not already registered.

        Returns:
            A complete system prompt for an LLM that should understand Notion-Markdown syntax
        """
        # Create a copy of registered elements
        element_classes = self._elements.copy()

        formatter_names = [e.__name__ for e in element_classes]
        if "TextInlineFormatter" not in formatter_names:
            element_classes = [TextInlineFormatter] + element_classes

        return MarkdownSyntaxPromptBuilder.generate_system_prompt(element_classes)


class MarkdownSyntaxPromptBuilder:
    """
    Generator for LLM system prompts that describe Notion-Markdown syntax.

    This class extracts information about supported Markdown patterns
    and formats them optimally for LLMs.
    """

    # Standard system prompt template
    SYSTEM_PROMPT_TEMPLATE = """You are a knowledgeable assistant that helps users create content for Notion pages.
Notion supports standard Markdown with some special extensions for creating rich content.

{element_docs}

Important usage guidelines:

1. The backtick code fence syntax (```) should ONLY be used when creating actual code blocks or diagrams.
Do not wrap examples or regular content in backticks unless you're showing code.

2. Use inline formatting (bold, italic, highlights, etc.) across all content to enhance readability.
The highlight syntax (==text== and ==color:text==) is especially useful for emphasizing important points.

3. Notion's extensions to Markdown (like callouts, bookmarks, toggles) provide richer formatting options
than standard Markdown while maintaining the familiar Markdown syntax for basic elements.

4. You can use these Markdown extensions alongside standard Markdown to create visually appealing
and well-structured content.

5. Remember that features like highlighting with ==yellow:important== work in all text blocks including
paragraphs, lists, quotes, etc.
"""

    @staticmethod
    def generate_element_doc(element_class: Type[NotionBlockElement]) -> str:
        """
        Generates documentation for a specific NotionBlockElement.

        Uses the element's get_llm_prompt_content method if available.
        """
        class_name = element_class.__name__
        element_name = class_name.replace("Element", "")

        # Start with element name as header
        result = [f"## {element_name}"]

        # Use get_llm_prompt_content if available
        if hasattr(element_class, "get_llm_prompt_content") and callable(
            getattr(element_class, "get_llm_prompt_content")
        ):
            content = element_class.get_llm_prompt_content()

            if content.get("description"):
                result.append(content["description"])

            if content.get("syntax"):
                result.append("\n### Syntax:")
                for syntax_item in content["syntax"]:
                    result.append(f"{syntax_item}")

            if content.get("examples"):
                result.append("\n### Examples:")
                for example in content["examples"]:
                    result.append(example)

            # Add any additional custom sections
            for key, value in content.items():
                if key not in ["description", "syntax", "examples"] and isinstance(
                    value, str
                ):
                    result.append(f"\n### {key.replace('_', ' ').title()}:")
                    result.append(value)

        return "\n".join(result)

    @classmethod
    def generate_element_docs(
        cls,
        element_classes: List[Type[NotionBlockElement]],
    ) -> str:
        """
        Generates complete documentation for all provided element classes.

        Args:
            element_classes: List of NotionBlockElement classes

        Returns:
            Documentation text for all elements
        """
        docs = [
            "# Custom Markdown Syntax for Notion Blocks",
            "The following custom Markdown patterns are supported for creating Notion blocks:",
        ]

        text_formatter = None
        other_elements = []

        for element in element_classes:
            if element.__name__ == "TextInlineFormatter":
                text_formatter = element
            else:
                other_elements.append(element)

        if text_formatter:
            docs.append("\n" + cls.generate_element_doc(text_formatter))

        for element in other_elements:
            if element.__name__ != "InlineFormattingElement":
                docs.append("\n" + cls.generate_element_doc(element))

        return "\n".join(docs)

    @classmethod
    def generate_system_prompt(
        cls,
        element_classes: List[Type[NotionBlockElement]],
    ) -> str:
        """
        Generates a complete system prompt for LLMs.

        Args:
            element_classes: List of element classes to document

        Returns:
            Complete system prompt for an LLM
        """
        element_docs = cls.generate_element_docs(element_classes)

        return cls.SYSTEM_PROMPT_TEMPLATE.format(element_docs=element_docs)
