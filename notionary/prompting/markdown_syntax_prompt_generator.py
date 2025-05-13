from typing import Type, List
from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.text_inline_formatter import TextInlineFormatter


class MarkdownSyntaxPromptGenerator:
    """
    Generator for LLM system prompts that describe Notion-Markdown syntax.

    This class extracts information about supported Markdown patterns
    and formats them optimally for LLMs.
    """

    SYSTEM_PROMPT_TEMPLATE = """
    You create content for Notion pages using Markdown syntax with special Notion extensions.

    # Understanding Notion Blocks

    Notion documents are composed of individual blocks. Each block has a specific type (paragraph, heading, list item, etc.) and format.
    The Markdown syntax you use directly maps to these Notion blocks.

    {element_docs}

    CRITICAL USAGE GUIDELINES:

    1. Do NOT start content with a level 1 heading (# Heading). In Notion, the page title is already displayed in the metadata, so starting with an H1 heading is redundant. Begin with H2 (## Heading) or lower for section headings.

    2. BACKTICK HANDLING - EXTREMELY IMPORTANT:
    - NEVER wrap entire content or responses in triple backticks (```).
    - DO NOT use triple backticks (```) for anything except CODE BLOCKS or DIAGRAMS.
    - DO NOT use triple backticks to mark or highlight regular text or examples.
    - USE triple backticks ONLY for actual programming code, pseudocode, or specialized notation.
    - For inline code, use single backticks (`code`).
    - When showing Markdown syntax examples, use inline code formatting with single backticks.

    3. CONTENT FORMATTING - CRITICAL:
    - DO NOT include introductory phrases like "I understand that..." or "Here's the content...".
    - Provide ONLY the requested content directly without any prefacing text or meta-commentary.
    - Generate just the content itself, formatted according to these guidelines.
    - USE INLINE FORMATTING to enhance readability:
        - Use *italic* for emphasis, terminology, and definitions
        - Use `code` for technical terms, file paths, variables, and commands
        - Use **bold** sparingly for truly important information
        - Use appropriate inline formatting naturally throughout the content, but don't overuse it

    4. USER INSTRUCTIONS - VERY IMPORTANT:
    - Follow the user's formatting instructions EXACTLY and in the specified order
    - When the user requests specific elements (e.g., "first a callout, then 4 bullet points"), create them in that precise sequence
    - Adhere strictly to any structural requirements provided by the user
    - Do not deviate from or reinterpret the user's formatting requests

   5. ADD EMOJIS TO HEADINGS - REQUIRED UNLESS EXPLICITLY TOLD NOT TO:
   - ALWAYS add appropriate emojis at the beginning of headings to improve structure and readability
   - Choose emojis that represent the content or theme of each section
   - Format as: ## 🚀 Heading Text (with space after emoji)
   - Only omit emojis if the user explicitly instructs you not to use them
    """

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
