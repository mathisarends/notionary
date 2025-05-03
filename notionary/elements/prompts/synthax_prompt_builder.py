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

# Understanding Notion Blocks
Notion documents are composed of individual blocks. Each block has a specific type (paragraph, heading, list item, etc.) and format. 
The Markdown syntax you use directly maps to these Notion blocks.

## Inline Formatting
Inline formatting can be used within most block types to style your text. You can combine multiple formatting options.
**Syntax:** **bold**, *italic*, `code`, ~~strikethrough~~, __underline__, [text](url)
**Examples:** 
- This text has a **bold** word.
- This text has an *italic* word.
- This text has `code` formatting.
- This text has ~~strikethrough~~ formatting.
- This text has __underlined__ formatting.
- This has a [hyperlink](https://example.com).
- You can **combine *different* formatting** styles.

**When to use:** Use inline formatting to highlight important words, provide emphasis, show code or paths, or add hyperlinks. This helps create visual hierarchy and improves scanability.

## Spacers and Block Separation
There are two ways to create visual separation between blocks:

1. **Empty Lines**: Simply add a blank line between blocks
   **Syntax:** Press Enter twice between blocks
   **Example:** 
   First paragraph.

   Second paragraph after an empty line.

2. **HTML Comment Spacer**: For more deliberate spacing between logical sections
   **Syntax:** <!-- spacer -->
   **Example:**
   ## First Section
   Content here.
   <!-- spacer -->
   ## Second Section
   More content here.

**When to use:** Use empty lines for basic separation between blocks. Use the HTML comment spacer (<!-- spacer -->) to create more obvious visual separation between major logical sections of your document.

{element_docs}

CRITICAL USAGE GUIDELINES:

1. Do NOT start content with a level 1 heading (# Heading). In Notion, the page title is already displayed in the metadata, so starting with an H1 heading is redundant. Begin with H2 (## Heading) or lower for section headings.

2. INLINE FORMATTING - VERY IMPORTANT:
   ✅ You can use inline formatting within almost any block type.
   ✅ Combine **bold**, *italic*, `code`, and other formatting as needed.
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
   ✅ For major logical sections, add the HTML comment spacer: <!-- spacer -->
   ✅ This spacer creates better visual breaks between key sections of your document.
   ⚠️ While headings can sometimes work without an empty line before the following paragraph, including empty lines between all block types ensures consistent rendering.

5. TOGGLE BLOCKS - NOTE:
   ✅ For toggle blocks and collapsible headings, use pipe prefixes (|) for content.
   ✅ Each line within a toggle should start with a pipe character followed by a space.
   ❌ Do not use the pipe character for any other blocks.

6. CONTENT FORMATTING - CRITICAL:
   ❌ DO NOT include introductory phrases like "I understand that..." or "Here's the content...".
   ✅ Provide ONLY the requested content directly without any prefacing text or meta-commentary.
   ✅ Generate just the content itself, formatted according to these guidelines.
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

        doc_parts = [
            f"## {element_name}",
            f"{content.description}",
            f"**Syntax:** {content.syntax}",
            f"**Example:** {content.examples[0]}" if content.examples else "",
            f"**When to use:** {content.when_to_use}",
        ]

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
