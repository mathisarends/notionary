from typing import TypedDict, List


class ElementPromptContent(TypedDict):
    """
    Typed dictionary defining the standardized structure for element prompt content.
    This ensures consistent formatting across all Notion block elements.
    """

    description: str
    """Concise explanation of what the element is and its purpose in Notion."""

    syntax: str
    """The exact markdown syntax pattern used to create this element."""

    examples: List[str]
    """List of practical usage examples showing the element in context."""

    when_to_use: str
    """Guidelines explaining the appropriate scenarios for using this element."""
