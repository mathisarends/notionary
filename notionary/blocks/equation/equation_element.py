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
    Supports two markdown styles for Notion equation blocks:

    1) Bracket style (analog zu [video]):
       - [equation](E = mc^2)
       - [equation]("E = mc^2 + \\frac{a}{b}")  # quoted form erlaubt ')' & Newlines

    2) LaTeX block style:
       - $$E = mc^2$$                  (single line)
       - $$\\n... multi-line ...\\n$$  (multi-line)
    """

    # --- [equation](...) styles ---
    _BRACKET_QUOTED = re.compile(
        r'^\[equation\]\(\s*"(?P<expr_q>[^"]+)"\s*\)$',
        re.DOTALL,
    )
    _BRACKET_UNQUOTED = re.compile(
        r'^\[equation\]\(\s*(?P<expr_u>[^)]+?)\s*\)$'
    )

    _SINGLE_LINE = re.compile(r"^\$\$(?P<expr>[^$]+)\$\$$")
    _MULTI_LINE = re.compile(r"^\$\$\s*\n(?P<expr>[\s\S]*?)\n\$\$$", re.MULTILINE)

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        s = text.strip()
        return bool(
            cls._BRACKET_QUOTED.match(s)
            or cls._BRACKET_UNQUOTED.match(s)
            or cls._SINGLE_LINE.match(s)
            or cls._MULTI_LINE.match(s)
        )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "equation" and getattr(block, "equation", None) is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        s = text.strip()

        # 1) [equation]("...")  — bevorzugt, da robust gegen ')', Newlines
        m = cls._BRACKET_QUOTED.match(s)
        if m:
            expr = m.group("expr_q").strip()
            return CreateEquationBlock(equation=EquationBlock(expression=expr)) if expr else None

        # 2) [equation](...)
        m = cls._BRACKET_UNQUOTED.match(s)
        if m:
            expr = m.group("expr_u").strip()
            return CreateEquationBlock(equation=EquationBlock(expression=expr)) if expr else None

        # 3) $$ ... $$  (single line / multi-line)
        m = cls._SINGLE_LINE.match(s) or cls._MULTI_LINE.match(s)
        if m:
            expr = m.group("expr").strip()
            return CreateEquationBlock(equation=EquationBlock(expression=expr)) if expr else None

        return None

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "equation" or getattr(block, "equation", None) is None:
            return None

        expr = (block.equation.expression or "").strip()
        if not expr:
            return None

        # Use [equation](...) syntax as default.
        # Quote if the expression contains risky characters (')') or newlines.
        if ("\n" in expr) or (")" in expr):
            return f'[equation]("{expr}")'
        return f"[equation]({expr})"

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Renders LaTeX math as a Notion equation block.")
            .with_usage_guidelines(
                "Use [equation](...) for concise formulas; quote the expression if it contains ')' or newlines. "
                "Also supports $$...$$ block syntax."
            )
            .with_syntax('[equation](E = mc^2)  ·  [equation]("E = mc^2 + \\\\frac{a}{b}")  ·  $$E = mc^2$$')
            .with_examples(
                [
                    "[equation](E = mc^2)",
                    '[equation]("x = \\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}")',
                    "$$\n\\int_0^1 x^2 \\, dx = \\frac{1}{3}\n$$",
                ]
            )
            .build()
        )
