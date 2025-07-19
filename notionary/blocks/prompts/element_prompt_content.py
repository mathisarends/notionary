from dataclasses import field, dataclass
from typing import Optional, List


@dataclass
class ElementPromptContent:
    """
    Dataclass defining the standardized structure for element prompt content.
    This ensures consistent formatting across all Notion block elements.
    """

    description: str
    """Concise explanation of what the element is and its purpose in Notion."""

    syntax: str
    """The exact markdown syntax pattern used to create this element."""

    when_to_use: str
    """Guidelines explaining the appropriate scenarios for using this element."""

    examples: List[str] = field(default_factory=list)
    """List of practical usage examples showing the element in context."""

    avoid: Optional[str] = None
    """Optional field listing scenarios when this element should be avoided."""

    is_standard_markdown: bool = False
    """Indicates whether this element follows standard Markdown syntax (and does not require full examples)."""

    def __post_init__(self):
        """Validates that the content meets minimum requirements."""
        if not self.description:
            raise ValueError("Description is required")
        if not self.syntax:
            raise ValueError("Syntax is required")
        if not self.examples and not self.is_standard_markdown:
            raise ValueError(
                "At least one example is required unless it's standard markdown."
            )
        if not self.when_to_use:
            raise ValueError("Usage guidelines are required")
