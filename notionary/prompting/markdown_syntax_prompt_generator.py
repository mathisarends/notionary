import os
from pathlib import Path
from typing import Type, List
from notionary.elements.notion_block_element import NotionBlockElement


class MarkdownSyntaxPromptGenerator:
    """
    Generator for LLM system prompts that describe Notion-Markdown syntax.

    This class extracts information about supported Markdown patterns
    and formats them optimally for LLMs.
    """

    def __init__(self):
        # Lade das Template aus der Markdown-Datei
        self.SYSTEM_PROMPT_TEMPLATE = self._load_template()

    def _load_template(self) -> str:
        """
        Lädt das Prompt-Template aus der Markdown-Datei.
        """
        current_dir = Path(__file__).parent
        template_path = current_dir /  "res/notion_syntax_prompt.md"

        try:
            with open(template_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found at {template_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading template file: {e}")

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
        # Erstelle eine Instanz, um das Template zu laden
        instance = cls()
        element_docs = cls.generate_element_docs(element_classes)
        return instance.SYSTEM_PROMPT_TEMPLATE.format(element_docs=element_docs)
