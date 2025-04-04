from typing import Dict, Any, List, Type
import inspect

from notionary.converters.notion_block_element import NotionBlockElement

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
        
        Args:
            element_class: The NotionBlockElement subclass to document
            
        Returns:
            Formatted documentation string for the element
        """
        class_name = element_class.__name__
        doc = element_class.__doc__ or ""
        
        element_name = class_name.replace("Element", "")
        
        result = [f"## {element_name}"]
        
        clean_doc = inspect.cleandoc(doc)
        result.append(clean_doc)
        
        example = LLMDocumentationGenerator._get_example(element_class)
        if example:
            result.append("\n### Example:")
            result.append(f"```markdown\n{example}\n```")
        
        return "\n".join(result)
    
    @staticmethod
    def _get_example(element_class: Type[NotionBlockElement]) -> str:
        """
        Gets example Markdown for an element class.
        This can be extended to pull from a class attribute or generate examples.
        """
        # You could define these as class attributes in each element class
        # or generate them dynamically based on the element's patterns
        examples = {
            "CalloutElement": "!> [💡] This is a callout with the default light bulb emoji\n!> {blue_background} [🔔] This is a blue callout with a bell emoji",
            "CodeBlockElement": "```python\nprint('Hello, world!')\n```",
            "HeadingElement": "# Heading 1\n## Heading 2\n### Heading 3",
        }
        
        return examples.get(element_class.__name__, "")
    
    @staticmethod
    def generate_full_documentation(element_classes: List[Type[NotionBlockElement]]) -> str:
        print("element_classes" ,element_classes)
        """
        Generates complete documentation for all provided element classes.
        
        Args:
            element_classes: List of NotionBlockElement subclasses to document
            
        Returns:
            Complete documentation string for all elements
        """
        docs = ["# Custom Markdown Syntax for Notion Blocks", 
                "The following custom Markdown patterns are supported for creating Notion blocks:"]
        
        for element_class in element_classes:
            docs.append("\n" + LLMDocumentationGenerator.generate_element_doc(element_class))
        
        return "\n".join(docs)