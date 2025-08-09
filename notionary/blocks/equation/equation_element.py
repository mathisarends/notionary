from __future__ import annotations
from typing import Optional
import re

from notionary.blocks.block_types import BlockType
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.equation.equation_models import CreateEquationBlock, EquationBlock
from notionary.prompts import ElementPromptBuilder, ElementPromptContent
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
    def match_markdown(cls, text: str) -> bool:
        input_text = text.strip()
        return bool(
            cls._QUOTED_PATTERN.match(input_text)
            or cls._UNQUOTED_PATTERN.match(input_text)
        )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.EQUATION and block.equation

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        input_text = text.strip()

        # Try quoted form first: [equation]("...")
        quoted_match = cls._QUOTED_PATTERN.match(input_text)
        if quoted_match:
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
        unquoted_match = cls._UNQUOTED_PATTERN.match(input_text)
        if unquoted_match:
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

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Renders LaTeX math as a Notion equation block.")
            .with_usage_guidelines(
                "Use [equation](...) for inline formulas. "
                'If your expression contains ")" or a newline, use the quoted form: [equation]("...").'
            )
            .with_syntax(
                '[equation](E = mc^2)  ·  [equation]("x = \\\\frac{-b\\\\pm\\\\sqrt{b^2-4ac}}{2a}")'
            )
            .with_examples(
                [
                    "[equation](E = mc^2)",
                    '[equation]("f(x) = \\sin(x) + \\cos(x)")',
                    '[equation]("P(A \\mid B) = \\frac{P(A \\cap B)}{P(B)}")',
                ]
            )
            .build()
        )
