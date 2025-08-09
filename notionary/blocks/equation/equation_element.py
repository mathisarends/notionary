from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import re

from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.equation.equation_models import CreateEquationBlock, EquationBlock
from notionary.prompts import ElementPromptBuilder, ElementPromptContent

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult


class EquationElement(NotionBlockElement):
    """
    Only supports bracket style (analog zu [video]):

      - [equation](E = mc^2)                    # unquoted: keine ')' oder Newlines
      - [equation]("E = mc^2 + \\frac{a}{b}")   # quoted: erlaubt ')' & Newlines & \"

    No $$...$$ parsing.
    """

    _BRACKET_QUOTED = re.compile(
        r'^\[equation\]\(\s*"(?P<expr_q>(?:[^"\\]|\\.)+)"\s*\)$',
        re.DOTALL,
    )

    # Unquoted: bis zur ersten ')', keine Newlines
    _BRACKET_UNQUOTED = re.compile(r"^\[equation\]\(\s*(?P<expr_u>[^)\r\n]+?)\s*\)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        s = text.strip()
        return bool(cls._BRACKET_QUOTED.match(s) or cls._BRACKET_UNQUOTED.match(s))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "equation" and getattr(block, "equation", None) is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        s = text.strip()

        # [equation]("...")  — robust (erlaubt ')', Newlines, \" usw.)
        m = cls._BRACKET_QUOTED.match(s)
        if m:
            expr = m.group("expr_q")
            # Unescape \" and \\ for Notion
            expr = expr.encode("utf-8").decode("unicode_escape")
            expr = expr.replace('\\"', '"')  # falls unicode_escape nicht alles greift
            return (
                CreateEquationBlock(equation=EquationBlock(expression=expr.strip()))
                if expr.strip()
                else None
            )

        # [equation](...)
        m = cls._BRACKET_UNQUOTED.match(s)
        if m:
            expr = m.group("expr_u").strip()
            # Hard rule: unquoted darf kein ')' und keinen Newline enthalten (Regex stellt das sicher)
            return (
                CreateEquationBlock(equation=EquationBlock(expression=expr))
                if expr
                else None
            )

        return None

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "equation" or getattr(block, "equation", None) is None:
            return None

        expr = (block.equation.expression or "").strip()
        if not expr:
            return None

        # Wenn riskante Zeichen vorkommen, quoted-Form verwenden
        if ("\n" in expr) or (")" in expr) or ('"' in expr):
            q = expr.replace("\\", "\\\\").replace('"', r"\"")
            return f'[equation]("{q}")'
        return f"[equation]({expr})"

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
