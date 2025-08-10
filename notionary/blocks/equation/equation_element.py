from __future__ import annotations
from typing import Optional
import re

from notionary.blocks.block_types import BlockType
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.equation.equation_models import CreateEquationBlock, EquationBlock

from notionary.blocks.block_models import Block, BlockCreateResult


class EquationElement(NotionBlockElement):
    """
    Only supports bracket style (analog zu [video]):

      - [equation](E = mc^2)                    # unquoted: keine ')' oder Newlines
      - [equation]("E = mc^2 + \\frac{a}{b}")   # quoted: erlaubt ')' & Newlines & \"

    No $$...$$ parsing.
    """

    _QUOTED_PATTERN = re.compile(
        r'^\[equation\]\(\s*"(?P<quoted_expr>(?:[^"\\]|\\.)*)"\s*\)$',
        re.DOTALL,
    )

    _UNQUOTED_PATTERN = re.compile(
        r"^\[equation\]\(\s*(?P<unquoted_expr>[^)\r\n]+?)\s*\)$"
    )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.EQUATION and block.equation

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        input_text = text.strip()

        # Try quoted form first: [equation]("...")
        if quoted_match := cls._QUOTED_PATTERN.match(input_text):
            raw_expression = quoted_match.group("quoted_expr")
            # Unescape \" and \\ for Notion
            unescaped_expression = raw_expression.encode("utf-8").decode(
                "unicode_escape"
            )
            unescaped_expression = unescaped_expression.replace('\\"', '"')
            final_expression = unescaped_expression.strip()

            return (
                CreateEquationBlock(equation=EquationBlock(expression=final_expression))
                if final_expression
                else None
            )

        # Try unquoted form: [equation](...)
        if unquoted_match := cls._UNQUOTED_PATTERN.match(input_text):
            raw_expression = unquoted_match.group("unquoted_expr").strip()
            return (
                CreateEquationBlock(equation=EquationBlock(expression=raw_expression))
                if raw_expression
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

        # Use quoted form if expression contains risky characters
        if ("\n" in expression) or (")" in expression) or ('"' in expression):
            escaped_expression = expression.replace("\\", "\\\\").replace('"', r"\"")
            return f'[equation]("{escaped_expression}")'

        return f"[equation]({expression})"
