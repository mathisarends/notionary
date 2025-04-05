import importlib
import inspect
import os
import pkgutil
from typing import List, Type, Dict, Any

from notionary.converters.notion_block_element import NotionBlockElement


class InlineFormattingElement:
    """
    Handles inline text formatting for Notion content.
    
    Supports various formatting options:
    - Bold: **text**
    - Italic: *text* or _text_
    - Underline: __text__
    - Strikethrough: ~~text~~
    - Code: `text`
    - Links: [text](url)
    - Highlights: ==text== (default yellow) or ==color:text== (custom color)
    """
    
    @classmethod
    def get_llm_prompt_content(cls) -> Dict[str, Any]:
        """
        Returns information about inline text formatting capabilities for LLM prompts.
        
        This method provides documentation about supported inline formatting options
        that can be used across all block elements.
        
        Returns:
            A dictionary with descriptions, syntax examples, and usage guidelines
        """
        return {
            "description": "Standard Markdown formatting is supported in all text blocks. Additionally, a custom highlight syntax is available for emphasizing important information. To create vertical spacing between elements, use the special spacer tag.",
            
            "syntax": [
                "**text** - Bold text",
                "*text* or _text_ - Italic text",
                "__text__ - Underlined text",
                "~~text~~ - Strikethrough text",
                "`text` - Inline code",
                "[text](url) - Link",
                "==text== - Default highlight (yellow background)",
                "==color:text== - Colored highlight (e.g., ==red:warning==)",
                "<!-- spacer --> - Creates vertical spacing between elements"
            ],
            
            "examples": [
                "This is a **bold** statement with some *italic* words.",
                "This feature is ~~deprecated~~ as of version 2.0.",
                "Edit the `config.json` file to configure settings.",
                "Check our [documentation](https://docs.example.com) for more details.",
                "==This is an important note== that you should remember.",
                "==red:Warning:== This action cannot be undone.",
                "==blue:Note:== Common colors include red, blue, green, yellow, purple.",
                "First paragraph content.\n\n<!-- spacer -->\n\nSecond paragraph with additional spacing above."
            ],
            
            "highlight_usage": "The highlight syntax (==text== and ==color:text==) should be used to emphasize important information, warnings, notes, or other content that needs to stand out. This is particularly useful for making content more scannable at a glance.",
            
            "spacer_usage": "Use the <!-- spacer --> tag on its own line to create additional vertical spacing between elements. This is useful for improving readability by visually separating sections of content. Multiple spacer tags can be used for greater spacing."
        }

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
                    result.append(f"- {syntax_item}")
            
            if content.get("examples"):
                result.append("\n### Examples:")
                for example in content["examples"]:
                    result.append(example)
            
            if content.get("highlight_usage"):
                result.append("\n### Highlight Usage:")
                result.append(content["highlight_usage"])
        
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
        
        docs.append("\n" + LLMDocumentationGenerator.generate_element_doc(InlineFormattingElement))
        
        # Add all other element classes
        for element_class in element_classes:
            if element_class.__name__ != "InlineFormattingElement":
                docs.append("\n" + LLMDocumentationGenerator.generate_element_doc(element_class))
        
        return "\n".join(docs)


class NotionLLMPromptGenerator:
    """
    Generates system prompts for LLM agents that can create Notion content
    using custom Markdown syntax. Uses auto-discovery to find all available
    NotionBlockElement classes.
    """
    
    @staticmethod
    def discover_element_classes(package_path: str) -> List[Type[NotionBlockElement]]:
        """
        Automatically discovers all NotionBlockElement subclasses in the specified package.
        
        Args:
            package_path: The import path to the package containing element classes
                         (e.g., "notionary.converters.elements")
        
        Returns:
            List of discovered NotionBlockElement subclass types
        """
        element_classes = []
        
        try:
            package = importlib.import_module(package_path)
            
            if hasattr(package, '__path__'):
                package_path_dirs = package.__path__
            else:
                package_path_dirs = [os.path.dirname(package.__file__)]
            
            for _, module_name, is_pkg in pkgutil.iter_modules(package_path_dirs):
                if is_pkg:
                    continue
                    
                module_full_name = f"{package_path}.{module_name}"
                module = importlib.import_module(module_full_name)
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, NotionBlockElement) and 
                        obj != NotionBlockElement):
                        element_classes.append(obj)
        except ImportError as e:
            print(f"Error importing package {package_path}: {e}")
        except Exception as e:
            print(f"Error during auto-discovery: {e}")
            
        return element_classes
    
    @staticmethod
    def generate_system_prompt(
        package_path: str = "notionary.converters.elements",
        include_inline_formatting: bool = True
    ) -> str:
        """
        Generates a complete system prompt for an LLM agent that works with Notion.
        Automatically discovers all available NotionBlockElement classes.
        
        Args:
            package_path: The import path to the package containing element classes
            print_output: Whether to print the generated system prompt
            include_inline_formatting: Whether to include InlineFormattingElement documentation
            
        Returns:
            Complete system prompt string with documentation for all discovered elements
        """
        # Discover all element classes in the specified package
        element_classes = NotionLLMPromptGenerator.discover_element_classes(package_path)
        
        if not element_classes:
            print(f"Warning: No NotionBlockElement subclasses found in package {package_path}")
            return "No Notion block elements found."
        
        if include_inline_formatting:
            element_classes = [InlineFormattingElement] + element_classes
        
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
    prompt = NotionLLMPromptGenerator.generate_system_prompt()
    print(prompt)