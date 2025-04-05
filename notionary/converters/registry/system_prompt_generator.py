from typing import List, Type, Optional

from notionary.converters.elements.notion_block_element import NotionBlockElement
from notionary.converters.elements.text_inline_formatter import TextInlineFormatter
from notionary.converters.registry.notion_element_registry import ElementRegistry


class LLMDocumentationGenerator:
    """
    Generates documentation for NotionBlockElements to be used in LLM system prompts.
    This class extracts information about custom Markdown patterns and formats it
    in a way that's optimized for LLM understanding.
    """
    
    @staticmethod
    def generate_element_doc(element_class: Type[NotionBlockElement]) -> str:
        """
        Generates documentation for a specific NotionBlockElement subclass.
        Prioritizes the get_llm_prompt_content method if available, otherwise falls back to docstring.
        """
        class_name = element_class.__name__
        element_name = class_name.replace("Element", "")
        
        # Start with element name as header
        result = [f"## {element_name}"]
        
        # Use get_llm_prompt_content if available
        if hasattr(element_class, 'get_llm_prompt_content') and callable(getattr(element_class, 'get_llm_prompt_content')):
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
                if key not in ["description", "syntax", "examples"] and isinstance(value, str):
                    result.append(f"\n### {key.replace('_', ' ').title()}:")
                    result.append(value)
        
        return "\n".join(result)
    
    
    @staticmethod
    def generate_full_documentation(element_classes: List[Type[NotionBlockElement]]) -> str:
        """
        Generates complete documentation for all provided element classes.
        
        Args:
            element_classes: List of NotionBlockElement subclasses to document
            
        Returns:
            Complete documentation string for all elements
        """
        docs = ["# Custom Markdown Syntax for Notion Blocks", 
                "The following custom Markdown patterns are supported for creating Notion blocks:"]
        
        docs.append("\n" + LLMDocumentationGenerator.generate_element_doc(TextInlineFormatter))
        
        for element_class in element_classes:
            if element_class.__name__ != "InlineFormattingElement":
                docs.append("\n" + LLMDocumentationGenerator.generate_element_doc(element_class))
        
        return "\n".join(docs)


class NotionLLMPromptGenerator:
    """
    Generates system prompts for LLM agents that can create Notion content
    using custom Markdown syntax. Uses the ElementRegistry to get all
    registered NotionBlockElement classes.
    """
    
    @staticmethod
    def generate_system_prompt(
        include_inline_formatting: bool = True,
        custom_registry: Optional[ElementRegistry] = None
    ) -> str:
        """
        Generates a complete system prompt for an LLM agent that works with Notion.
        Uses all registered elements from the ElementRegistry.
        
        Args:
            include_inline_formatting: Whether to include InlineFormattingElement documentation
            custom_registry: Optional custom registry to use instead of the default one
            
        Returns:
            Complete system prompt string with documentation for all registered elements
        """
        # Get all registered elements from the registry
        registry = custom_registry or ElementRegistry
        element_classes = registry.get_elements()
        
        if not element_classes:
            print("Warning: No elements are registered in the ElementRegistry")
            return "No Notion block elements registered."
        
        if include_inline_formatting:
            # Add InlineFormattingElement if not already in the list
            format_element_names = [e.__name__ for e in element_classes]
            if "InlineFormattingElement" not in format_element_names:
                element_classes = [TextInlineFormatter] + element_classes
        
        element_docs = LLMDocumentationGenerator.generate_full_documentation(element_classes)
        
        system_prompt_template = """You are a knowledgeable assistant that helps users create content for Notion pages.
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
        final_prompt = system_prompt_template.format(element_docs=element_docs)
        
        return final_prompt


# Beispiel für die Verwendung mit einer konfigurierbaren Registry
class ConfigurableNotionPromptGenerator:
    """
    A version of the prompt generator that works with configurable registries,
    allowing users to generate documentation for only specific elements.
    """
    
    @staticmethod
    def create_prompt_for_elements(
        element_classes: List[Type[NotionBlockElement]], 
        include_inline_formatting: bool = True
    ) -> str:
        """
        Creates a system prompt for specific element classes.
        
        Args:
            element_classes: The specific element classes to include
            include_inline_formatting: Whether to include inline formatting docs
            
        Returns:
            System prompt for the specified elements
        """
        if include_inline_formatting:
            # Check if InlineFormattingElement is included
            format_included = any(e.__name__ == "InlineFormattingElement" for e in element_classes)
            if not format_included:
                element_classes = [TextInlineFormatter] + element_classes
        
        element_docs = LLMDocumentationGenerator.generate_full_documentation(element_classes)
        
        system_prompt_template = """You are a knowledgeable assistant that helps users create content for Notion pages.
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
        final_prompt = system_prompt_template.format(element_docs=element_docs)
        
        return final_prompt


# Example usage
if __name__ == "__main__":
    # Standard usage with the default ElementRegistry
    prompt = NotionLLMPromptGenerator.generate_system_prompt()
    print(prompt)