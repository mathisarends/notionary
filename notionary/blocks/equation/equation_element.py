from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.equation.equation_models import CreateEquationBlock, EquationBlock
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult
from notionary.blocks.types import BlockType


class EquationElement(BaseBlockElement):
    """
    Supports standard Markdown equation syntax:

      - $$E = mc^2$$                           # simple equations
      - $$E = mc^2 + \\frac{a}{b}$$           # complex equations with LaTeX

    Uses $$...$$ parsing for block equations.
    """

    _EQUATION_PATTERN = re.compile(
        r'^\$\$\s*(?P<expression>.*?)\s*\$\$$',
        re.DOTALL,
    )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.EQUATION and block.equation

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        input_text = text.strip()

        # Try $$...$$ pattern
        if equation_match := cls._EQUATION_PATTERN.match(input_text):
            expression = equation_match.group("expression").strip()
            return (
                CreateEquationBlock(equation=EquationBlock(expression=expression))
                if expression
                else None
            )

        return None

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.EQUATION or not block.equation:
            return None

        expression = (block.equation.expression or "").strip()
        if not expression:
            return None

        return f"$${expression}$$"

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for equation blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Mathematical equations using standard Markdown LaTeX syntax",
            syntax_examples=[
                "$$E = mc^2$$",
                "$$\\frac{a}{b} + \\sqrt{c}$$",
                "$$\\int_0^\\infty e^{-x} dx = 1$$",
                "$$\\sum_{i=1}^n i = \\frac{n(n+1)}{2}$$",
            ],
            usage_guidelines="Use for mathematical expressions and formulas. Supports LaTeX syntax. Wrap equations in double dollar signs ($$).",
        )
