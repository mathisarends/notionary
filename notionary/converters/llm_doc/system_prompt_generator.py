import importlib
import inspect
import os
import pkgutil
from typing import List, Type

from notionary.converters.notion_block_element import NotionBlockElement
from llm_documentation_generator import LLMDocumentationGenerator

class SystemPromptGenerator:
    """
    Generates system prompts for LLM agents that interact with Notion pages
    using custom Markdown syntax.
    """
    
    @staticmethod
    def discover_element_classes(elements_package_path: str) -> List[Type[NotionBlockElement]]:
        """
        Discovers all NotionBlockElement subclasses in the given package.
        
        Args:
            elements_package_path: The import path to the package containing element classes
                                  e.g., "notionary.converters.elements"
        
        Returns:
            List of discovered NotionBlockElement subclass types
        """
        element_classes = []
        
        # Import the package
        package = importlib.import_module(elements_package_path)
        package_dir = os.path.dirname(package.__file__)
        
        # Iterate through all modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
            if is_pkg:
                continue
                
            # Import the module
            module = importlib.import_module(f"{elements_package_path}.{module_name}")
            
            # Find all classes in the module that inherit from NotionBlockElement
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, NotionBlockElement) and 
                    obj != NotionBlockElement):
                    element_classes.append(obj)
        
        return element_classes
    
    @staticmethod
    def generate_system_prompt(elements_package_path: str = "notionary.converters.elements") -> str:
        """
        Generates a complete system prompt for an LLM agent that works with Notion.
        
        Args:
            elements_package_path: The import path to the package containing element classes
        
        Returns:
            Complete system prompt string
        """
        # Discover all element classes
        element_classes = SystemPromptGenerator.discover_element_classes(elements_package_path)
        
        # Generate documentation for all elements
        element_docs = LLMDocumentationGenerator.generate_full_documentation(element_classes)
        
        # Combine into a complete system prompt
        system_prompt = f"""
You are a knowledgeable assistant that helps users create content for Notion pages.
When creating content, you should use the custom Markdown syntax defined below to 
create properly formatted Notion blocks.

{element_docs}

When writing content, prefer using these specialized Markdown formats over regular Markdown
when appropriate. This will ensure the content is properly converted to Notion blocks.

Always format your response using the appropriate Markdown syntax for the content type.
For example, use callouts for important information, code blocks for code, etc.

Remember that multiline blocks (like code blocks) require proper opening and closing syntax.
"""
        
        return system_prompt.strip()
    
    @staticmethod
    def save_system_prompt(output_path: str, elements_package_path: str = "notionary.converters.elements"):
        """
        Generates and saves the system prompt to a file.
        
        Args:
            output_path: Path where the system prompt should be saved
            elements_package_path: The import path to the package containing element classes
        """
        system_prompt = SystemPromptGenerator.generate_system_prompt(elements_package_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(system_prompt)
            
        print(f"System prompt saved to {output_path}")


# Example usage
if __name__ == "__main__":
    # Generate and save the system prompt
    SystemPromptGenerator.save_system_prompt("notion_llm_system_prompt.txt")
    
    # Or, to just print the system prompt:
    # print(SystemPromptGenerator.generate_system_prompt())