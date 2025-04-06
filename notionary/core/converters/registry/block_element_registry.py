from typing import Dict, Any, Optional, List, Type

from notionary.core.converters.elements.notion_block_element import NotionBlockElement
from notionary.core.converters.elements.text_inline_formatter import TextInlineFormatter

# TODO: Das hier nicht mehr in einem Singleton verwenden, sondern in Instanzen die man dann auf unterschiedliche Arten bauen kann mit einem Builder oder Fabrik Muster.
class BlockElementRegistry:
    """Registry of elements that can convert between Markdown and Notion."""

    _elements = []

    @classmethod
    def register(cls, element_class: Type[NotionBlockElement]):
        """Register an element class."""
        cls._elements.append(element_class)

    @classmethod
    def deregister(cls, element_class: Type[NotionBlockElement]) -> bool:
        """
        Deregister an element class.

        Args:
            element_class: The element class to remove from the registry

        Returns:
            bool: True if the element was removed, False if it wasn't in the registry
        """
        if element_class in cls._elements:
            cls._elements.remove(element_class)
            return True
        return False
    
    @classmethod
    def clear(cls):
        """Leert die Registry komplett."""
        cls._elements.clear()

    @classmethod
    def find_markdown_handler(cls, text: str) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given markdown text."""
        for element in cls._elements:
            if element.match_markdown(text):
                return element
        return None

    @classmethod
    def find_notion_handler(
        cls, block: Dict[str, Any]
    ) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given Notion block."""
        for element in cls._elements:
            if element.match_notion(block):
                return element
        return None

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block using registered elements."""
        handler = cls.find_markdown_handler(text)
        if handler:
            return handler.markdown_to_notion(text)
        return None

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown using registered elements."""
        handler = cls.find_notion_handler(block)
        if handler:
            return handler.notion_to_markdown(block)
        return None

    @classmethod
    def get_multiline_elements(cls) -> List[Type[NotionBlockElement]]:
        """Get all registered multiline elements."""
        return [element for element in cls._elements if element.is_multiline()]

    @classmethod
    def get_elements(cls) -> List[Type[NotionBlockElement]]:
        """Get all registered elements."""
        return cls._elements.copy()
    
    @classmethod
    def generate_llm_prompt(cls) -> str:
        """
        Generiert einen LLM-System-Prompt, der die Markdown-Syntax aller registrierten Elemente beschreibt.
        
        Es wird automatisch der TextInlineFormatter hinzugefügt, falls er nicht bereits registriert ist.
        
        Returns:
            Ein kompletter System-Prompt für ein LLM, das Notion-Markdown-Syntax verstehen soll
        """
        # Kopie der registrierten Elemente erstellen
        element_classes = cls._elements.copy()
        print("Elemente in der Registry:", element_classes)
        
        formatter_names = [e.__name__ for e in element_classes]
        if "TextInlineFormatter" not in formatter_names:
            element_classes = [TextInlineFormatter] + element_classes
        
        return MarkdownSyntaxPromptBuilder.generate_system_prompt(element_classes)


# TODO: Das muss hier besser benannt werden
class MarkdownSyntaxPromptBuilder:
    """
    Generator für LLM-System-Prompts, die Notion-Markdown-Syntax beschreiben.
    
    Diese Klasse extrahiert Informationen über unterstützte Markdown-Patterns
    und formatiert sie für LLMs optimal.
    """
    
    # Standard System-Prompt Template
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
        Generiert Dokumentation für ein spezifisches NotionBlockElement.
        
        Verwendet die get_llm_prompt_content-Methode des Elements, wenn verfügbar.
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
        Generiert vollständige Dokumentation für alle übergebenen Element-Klassen.
        
        Args:
            element_classes: Liste von NotionBlockElement-Klassen
            
        Returns:
            Dokumentationstext für alle Elemente
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
        Generiert einen vollständigen System-Prompt für LLMs.
        
        Args:
            element_classes: Liste der zu dokumentierenden Element-Klassen
            
        Returns:
            Vollständiger System-Prompt für ein LLM
        """
        element_docs = cls.generate_element_docs(element_classes)
        
        return cls.SYSTEM_PROMPT_TEMPLATE.format(element_docs=element_docs)