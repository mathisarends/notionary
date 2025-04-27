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

Important usage guidelines:

1. Do NOT start content with a level 1 heading (# Heading). In Notion, the page title is already displayed in the metadata, so starting with an H1 heading is redundant. Begin with H2 (## Heading) or lower for section headings.

2. The backtick code fence syntax (```) should ONLY be used when creating actual code blocks or diagrams.
Do not wrap examples or regular content in backticks unless you're showing code.

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
        Generates documentation for a specific NotionBlockElement.
        Uses the element's get_llm_prompt_content method if available.
        """
        class_name = element_class.__name__
        element_name = class_name.replace("Element", "")
        result = [f"## {element_name}"]

        if not hasattr(element_class, "get_llm_prompt_content") or not callable(getattr(element_class, "get_llm_prompt_content")):
            return "\n".join(result)

        content = element_class.get_llm_prompt_content()

        result += MarkdownSyntaxPromptBuilder._generate_standard_sections(content)
        result += MarkdownSyntaxPromptBuilder._generate_custom_sections(content)

        return "\n".join(result)

    @staticmethod
    def _generate_standard_sections(content: dict) -> List[str]:
        """
        Generates standard sections like description, syntax, examples, guidelines.
        """
        result = []

        if content.get("description"):
            result.append(content["description"])

        if content.get("syntax"):
            result.append("\n### Syntax:")
            result.extend(content["syntax"])

        if content.get("examples"):
            result.append("\n### Examples:")
            result.extend(content["examples"])

        if content.get("guidelines"):
            result.append("\n### Guidelines:")
            result.extend(f"- {g}" for g in content["guidelines"])

        return result

    @staticmethod
    def _generate_custom_sections(content: dict) -> List[str]:
        """
        Generates additional sections that are not part of the standard set.
        """
        result = []
        standard_keys = {"description", "syntax", "examples", "guidelines"}

        for key, value in content.items():
            if key not in standard_keys and isinstance(value, str):
                result.append(f"\n### {key.replace('_', ' ').title()}:")
                result.append(value)

        return result

    @classmethod
    def generate_element_docs(cls, element_classes: List[Type[NotionBlockElement]]) -> str:
        """
        Generates complete documentation for all provided element classes.
        """
        docs = [
            "# Markdown Syntax for Notion Blocks",
            "The following Markdown patterns are supported for creating Notion blocks:",
        ]
        
        # Simply generate docs for each element
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