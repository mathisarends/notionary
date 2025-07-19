from typing import Optional, List, Self
from notionary.blocks.prompts.element_prompt_content import ElementPromptContent


class ElementPromptBuilder:
    """
    Builder class for creating ElementPromptContent with a fluent interface.
    Provides better IDE support and validation for creating prompts.
    """

    def __init__(self) -> None:
        self._description: Optional[str] = None
        self._syntax: Optional[str] = None
        self._examples: List[str] = []
        self._when_to_use: Optional[str] = None
        self._avoid: Optional[str] = None
        self._is_standard_markdown = False

    def with_description(self, description: str) -> Self:
        """Set the description of the element."""
        self._description = description
        return self

    def with_syntax(self, syntax: str) -> Self:
        """Set the syntax pattern for the element."""
        self._syntax = syntax
        return self

    def add_example(self, example: str) -> Self:
        """Add a usage example for the element."""
        self._examples.append(example)
        return self

    def with_examples(self, examples: List[str]) -> Self:
        """Set the list of usage examples for the element."""
        self._examples = examples.copy()
        return self

    def with_usage_guidelines(self, when_to_use: str) -> Self:
        """Set the usage guidelines for the element."""
        self._when_to_use = when_to_use
        return self

    def with_avoidance_guidelines(self, avoid: str) -> Self:
        """Set the scenarios when this element should be avoided."""
        self._avoid = avoid
        return self

    def with_standard_markdown(self) -> Self:
        """Indicate that this element follows standard Markdown syntax."""
        self._examples = []
        self._is_standard_markdown = True
        return self

    def build(self) -> ElementPromptContent:
        """
        Build and validate the ElementPromptContent object.

        Returns:
            A valid ElementPromptContent object.

        Raises:
            ValueError: If any required field is missing.
        """
        if not self._description:
            raise ValueError("Description is required")
        if not self._syntax:
            raise ValueError("Syntax is required")
        if not self._examples and not self._is_standard_markdown:
            raise ValueError(
                "At least one example is required unless it's standard markdown."
            )
        if not self._when_to_use:
            raise ValueError("Usage guidelines are required")

        return ElementPromptContent(
            description=self._description,
            syntax=self._syntax,
            examples=self._examples,
            when_to_use=self._when_to_use,
            avoid=self._avoid,
            is_standard_markdown=self._is_standard_markdown,
        )
