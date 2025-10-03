import re
import textwrap

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.schemas import Block, BlockType, CreateEquationBlock, EquationData
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class EquationMapper(NotionMarkdownMapper):
    """
    Supports standard Markdown equation syntax:

      - $$E = mc^2$$                           # simple equations
      - $$E = mc^2 + \\frac{a}{b}$$           # complex equations with LaTeX

    Uses $$...$$ parsing for block equations.
    """

    _EQUATION_PATTERN = re.compile(
        r"^\$\$\s*(?P<expression>.*?)\s*\$\$$",
        re.DOTALL,
    )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.EQUATION and block.equation

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateEquationBlock:
        input_text = text.strip()

        equation_match = cls._EQUATION_PATTERN.match(input_text)
        if not equation_match:
            return None

        expression = equation_match.group("expression").strip()
        if not expression:
            return None

        return CreateEquationBlock(equation=EquationData(expression=expression))

    @classmethod
    def create_from_markdown_block(cls, opening_line: str, equation_lines: list[str]) -> CreateEquationBlock:
        """
        Create a complete equation block from markdown components.
        Handles multiline equations like:
        $$
        some
        inline formula here
        $$

        Automatically handles:
        - Indentation removal from multiline strings
        - Single backslash conversion to double backslash for LaTeX line breaks
        """
        # Check if opening line is just $$
        if opening_line.strip() != "$$":
            return None

        # Process equation lines if any exist
        if equation_lines:
            # Remove common indentation from all lines
            raw_content = "\n".join(equation_lines)
            dedented_content = textwrap.dedent(raw_content)

            # Fix single backslashes at line ends for LaTeX line breaks
            fixed_lines = cls._fix_latex_line_breaks(dedented_content.splitlines())
            expression = "\n".join(fixed_lines).strip()

            if expression:
                return CreateEquationBlock(equation=EquationData(expression=expression))

        return None

    @classmethod
    def _fix_latex_line_breaks(cls, lines: list[str]) -> list[str]:
        """
        Fix lines that end with single backslashes by converting them to double backslashes.
        This makes LaTeX line breaks work correctly when users write single backslashes.

        Examples:
        - "a = b + c \" -> "a = b + c \\"
        - "a = b + c \\\\" -> "a = b + c \\\\" (unchanged)
        """
        fixed_lines = []

        for line in lines:
            # Check if line ends with backslashes
            backslash_match = re.search(r"(\\+)$", line)
            if backslash_match:
                backslashes = backslash_match.group(1)
                # If odd number of backslashes, the last one needs to be doubled
                if len(backslashes) % 2 == 1:
                    line = line + "\\"

            fixed_lines.append(line)

        return fixed_lines

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.EQUATION or not block.equation:
            return None

        expression = (block.equation.expression or "").strip()
        if not expression:
            return None

        return f"$${expression}$$"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
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
