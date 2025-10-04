from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
    Hier ist ein einfaches Beispiel:

    $$
    E = mc^2
    $$

    Oder komplexere Formeln:

    $$
    \\sum_{i=1}^n i = \frac{n(n+1)}{2}
    $$

    Auch mit Leerzeilen innerhalb:

    $$
    x = \frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}

    y = mx + c
    $$

    Mehrzeilige Matrix:

    $$
    \begin{pmatrix}
    a & b \\
    c & d
    \\end{pmatrix}
    \begin{pmatrix}
    x \\
    y
    \\end{pmatrix}
    =
    \begin{pmatrix}
    ax + by \\
    cx + dy
    \\end{pmatrix}
    $$

    Lange Gleichung mit Zeilenbruch:

    $$
    f(x) = \frac{1}{\\sqrt{2\\pi\\sigma^2}} \\exp\\left(-\frac{(x-\\mu)^2}{2\\sigma^2}\right) \\
    \text{für } x \\in \\mathbb{R}
    $$

    Komplexe Integralgleichung:

    $$
    \\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi} \\
    \\iint_D f(x,y) \\, dx \\, dy = \\lim_{n \to \\infty} \\sum_{i=1}^n f(x_i^*, y_i^*) \\Delta A_i
    $$
    """
    content = await page.append_markdown(markdown)
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
