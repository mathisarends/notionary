import pytest

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.inline_equation import (
    EquationHandler,
)
from notionary.rich_text.schemas import EquationObject, RichText, RichTextType


@pytest.fixture
def handler() -> EquationHandler:
    return EquationHandler(MarkdownGrammar())


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def expected_equation(markdown_grammar: MarkdownGrammar):
    def _format(expression: str) -> str:
        return (
            f"{markdown_grammar.inline_equation_wrapper}"
            f"{expression}"
            f"{markdown_grammar.inline_equation_wrapper}"
        )

    return _format


class TestEquationHandlerBasics:
    @pytest.mark.asyncio
    async def test_simple_equation(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression="E = mc^2"),
            plain_text="E = mc^2",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation("E = mc^2")

    @pytest.mark.asyncio
    async def test_empty_equation(
        self, handler: EquationHandler, markdown_grammar: MarkdownGrammar
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=""),
            plain_text="",
        )
        result = await handler.handle(rich_text)
        assert (
            result
            == f"{markdown_grammar.inline_equation_wrapper}{markdown_grammar.inline_equation_wrapper}"
        )

    @pytest.mark.asyncio
    async def test_equation_none(self, handler: EquationHandler) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=None,
            plain_text="",
        )
        result = await handler.handle(rich_text)
        assert result == ""


class TestEquationHandlerComplexExpressions:
    @pytest.mark.asyncio
    async def test_fraction_equation(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"\frac{1}{2}"),
            plain_text=r"\frac{1}{2}",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"\frac{1}{2}")

    @pytest.mark.asyncio
    async def test_integral_equation(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(
                expression=r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"
            ),
            plain_text=r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(
            r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"
        )

    @pytest.mark.asyncio
    async def test_sum_equation(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}"),
            plain_text=r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}")

    @pytest.mark.asyncio
    async def test_matrix_equation(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(
                expression=r"\begin{bmatrix}a & b\\c & d\end{bmatrix}"
            ),
            plain_text=r"\begin{bmatrix}a & b\\c & d\end{bmatrix}",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"\begin{bmatrix}a & b\\c & d\end{bmatrix}")

    @pytest.mark.asyncio
    async def test_limit_equation(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"\lim_{x \to \infty} \frac{1}{x} = 0"),
            plain_text=r"\lim_{x \to \infty} \frac{1}{x} = 0",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"\lim_{x \to \infty} \frac{1}{x} = 0")


class TestEquationHandlerSpecialCharacters:
    @pytest.mark.asyncio
    async def test_equation_with_greek_letters(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"\alpha + \beta = \gamma"),
            plain_text=r"\alpha + \beta = \gamma",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"\alpha + \beta = \gamma")

    @pytest.mark.asyncio
    async def test_equation_with_subscripts_superscripts(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"x^2 + y_1^3 = z_{12}^{34}"),
            plain_text=r"x^2 + y_1^3 = z_{12}^{34}",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"x^2 + y_1^3 = z_{12}^{34}")

    @pytest.mark.asyncio
    async def test_equation_with_symbols(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"\forall x \in \mathbb{R}: x^2 \geq 0"),
            plain_text=r"\forall x \in \mathbb{R}: x^2 \geq 0",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"\forall x \in \mathbb{R}: x^2 \geq 0")

    @pytest.mark.asyncio
    async def test_equation_with_brackets_and_parentheses(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(
                expression=r"\left[\frac{x}{y}\right] + \left(\frac{a}{b}\right)"
            ),
            plain_text=r"\left[\frac{x}{y}\right] + \left(\frac{a}{b}\right)",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(
            r"\left[\frac{x}{y}\right] + \left(\frac{a}{b}\right)"
        )


class TestEquationHandlerEdgeCases:
    @pytest.mark.asyncio
    async def test_equation_with_whitespace(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression="  x = y  "),
            plain_text="  x = y  ",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation("  x = y  ")

    @pytest.mark.asyncio
    async def test_equation_with_newlines(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression="x = y\ny = z"),
            plain_text="x = y\ny = z",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation("x = y\ny = z")

    @pytest.mark.asyncio
    async def test_single_variable(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression="x"),
            plain_text="x",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation("x")

    @pytest.mark.asyncio
    async def test_single_number(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression="42"),
            plain_text="42",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation("42")

    @pytest.mark.asyncio
    async def test_equation_with_special_chars_that_might_break_markdown(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression="*x* + **y** = `z`"),
            plain_text="*x* + **y** = `z`",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation("*x* + **y** = `z`")


class TestEquationHandlerGrammarConsistency:
    @pytest.mark.asyncio
    async def test_uses_grammar_wrapper(
        self, handler: EquationHandler, markdown_grammar: MarkdownGrammar
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression="a = b"),
            plain_text="a = b",
        )
        result = await handler.handle(rich_text)
        expected = (
            f"{markdown_grammar.inline_equation_wrapper}"
            f"a = b"
            f"{markdown_grammar.inline_equation_wrapper}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_wrapper_is_single_dollar(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.inline_equation_wrapper == "$"


class TestEquationHandlerRealWorldExamples:
    @pytest.mark.asyncio
    async def test_quadratic_formula(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(
                expression=r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"
            ),
            plain_text=r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")

    @pytest.mark.asyncio
    async def test_pythagorean_theorem(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"a^2 + b^2 = c^2"),
            plain_text=r"a^2 + b^2 = c^2",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"a^2 + b^2 = c^2")

    @pytest.mark.asyncio
    async def test_einstein_mass_energy(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=r"E = mc^2"),
            plain_text=r"E = mc^2",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(r"E = mc^2")

    @pytest.mark.asyncio
    async def test_normal_distribution(
        self, handler: EquationHandler, expected_equation
    ) -> None:
        rich_text = RichText(
            type=RichTextType.EQUATION,
            equation=EquationObject(
                expression=r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}"
            ),
            plain_text=r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}",
        )
        result = await handler.handle(rich_text)
        assert result == expected_equation(
            r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}"
        )
