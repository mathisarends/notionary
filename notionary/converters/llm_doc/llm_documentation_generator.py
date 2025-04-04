import importlib
import inspect
import os
import pkgutil
from typing import List, Type

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
        Prioritizes the get_llm_prompt_content method if available, otherwise falls back to docstring.
        
        Args:
            element_class: The NotionBlockElement subclass to document
            
        Returns:
            Formatted documentation string for the element
        """
        class_name = element_class.__name__
        element_name = class_name.replace("Element", "")
        
        result = [f"## {element_name}"]
        
        # Prioritize get_llm_prompt_content method if available
        if hasattr(element_class, 'get_llm_prompt_content') and callable(getattr(element_class, 'get_llm_prompt_content')):
            content = element_class.get_llm_prompt_content()
            
            # Add description
            if "description" in content:
                result.append(content["description"])
            
            # Add usage guidance
            if "when_to_use" in content:
                result.append(f"\n**When to use:** {content['when_to_use']}")
            
            # Add syntax options
            if "syntax" in content:
                result.append("\n### Syntax:")
                for syntax_item in content["syntax"]:
                    result.append(f"- `{syntax_item}`")
            
            # Add notes if available
            if "notes" in content:
                result.append("\n### Notes:")
                for note in content["notes"]:
                    result.append(f"- {note}")
            
            # Add color options if available (for elements with color support)
            if "color_options" in content:
                result.append("\n### Available colors:")
                colors = ", ".join(f"`{color}`" for color in content["color_options"])
                result.append(colors)
                
            # Add supported sources if available (for media elements)
            if "supported_sources" in content:
                result.append("\n### Supported sources:")
                for source in content["supported_sources"]:
                    result.append(f"- {source}")
            
            # Add examples
            if "examples" in content:
                result.append("\n### Examples:")
                result.append("```markdown")
                for example in content["examples"]:
                    result.append(example)
                result.append("```")
        
        # Fall back to docstring if get_llm_prompt_content is not available
        else:
            doc = element_class.__doc__ or ""
            clean_doc = inspect.cleandoc(doc)
            result.append(clean_doc)
            
            # Get example using the old method
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
            # Import the package
            package = importlib.import_module(package_path)
            
            # Get the package directory
            if hasattr(package, '__path__'):
                package_path_dirs = package.__path__
            else:
                package_path_dirs = [os.path.dirname(package.__file__)]
            
            # Iterate through all modules in the package
            for _, module_name, is_pkg in pkgutil.iter_modules(package_path_dirs):
                # Skip subpackages
                if is_pkg:
                    continue
                    
                # Import the module
                module_full_name = f"{package_path}.{module_name}"
                module = importlib.import_module(module_full_name)
                
                # Find all classes in the module that inherit from NotionBlockElement
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
        print_output: bool = False
    ) -> str:
        """
        Generates a complete system prompt for an LLM agent that works with Notion.
        Automatically discovers all available NotionBlockElement classes.
        
        Args:
            package_path: The import path to the package containing element classes
            print_output: Whether to print the generated system prompt
            
        Returns:
            Complete system prompt string with documentation for all discovered elements
        """
        # Discover all element classes in the specified package
        element_classes = NotionLLMPromptGenerator.discover_element_classes(package_path)
        
        if not element_classes:
            print(f"Warning: No NotionBlockElement subclasses found in package {package_path}")
            return "No Notion block elements found."
        
        # Generate documentation for all elements
        element_docs = LLMDocumentationGenerator.generate_full_documentation(element_classes)
        
        # Create the system prompt template with consistent indentation
        system_prompt_template = """You are a knowledgeable assistant that helps users create content for Notion pages.
When creating content, you should use the custom Markdown syntax defined below to 
create properly formatted Notion blocks.

{element_docs}

When writing content, prefer using these specialized Markdown formats over regular Markdown
when appropriate. This will ensure the content is properly converted to Notion blocks.

Always format your response using the appropriate Markdown syntax for the content type.
For example, use callouts for important information, code blocks for code, etc.

Remember that multiline blocks (like code blocks) require proper opening and closing syntax."""
        
        # Insert element docs into the template
        final_prompt = system_prompt_template.format(element_docs=element_docs)
        
        # Print if requested
        if print_output:
            print(final_prompt)
            
        return final_prompt


# Example usage
if __name__ == "__main__":
    # Generate system prompt with auto-discovery
    prompt = NotionLLMPromptGenerator.generate_system_prompt(print_output=True)
    
    # To save to a file if needed:
    # with open("notion_llm_system_prompt.txt", "w", encoding="utf-8") as f:
    #     f.write(prompt)