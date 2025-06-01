from functools import wraps
from typing import Dict, Any, Optional
from abc import ABC

from notionary.prompting.element_prompt_content import ElementPromptContent
from notionary.telemetry import track_usage


class NotionBlockElement(ABC):
    """Base class for elements that can be converted between Markdown and Notion."""

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block."""

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown."""

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return bool(cls.markdown_to_notion(text))  # Now calls the class's version

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return bool(cls.notion_to_markdown(block))  # Now calls the class's version

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns a dictionary with information for LLM prompts about this element."""


def auto_track_conversions(cls):
    """
    Decorator der sich auch auf Subklassen vererbt.
    """
    conversion_methods = ['markdown_to_notion', 'notion_to_markdown']
    
    original_init_subclass = getattr(cls, '__init_subclass__', None)
    
    @classmethod
    def __init_subclass__(cls_inner, **kwargs):
        # Original __init_subclass__ aufrufen
        if original_init_subclass:
            original_init_subclass(**kwargs)
        
        # Tracking für Subklasse hinzufügen
        for method_name in conversion_methods:
            if hasattr(cls_inner, method_name):
                original_method = getattr(cls_inner, method_name)
                
                if isinstance(original_method, classmethod):
                    func = original_method.__func__
                    
                    @track_usage(f"{cls_inner.__name__.lower()}_{method_name}")
                    @classmethod
                    @wraps(func)
                    def tracked_method(cls_ref, *args, **kwargs):
                        return func(cls_ref, *args, **kwargs)
                    
                    setattr(cls_inner, method_name, tracked_method)
    
    cls.__init_subclass__ = __init_subclass__
    return cls