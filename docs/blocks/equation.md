# Equation Blocks

Equation blocks render LaTeX-based math expressions. Ideal for technical docs, education, and research.

## Basic Syntax

```markdown
[equation](E = mc^2)
[equation](x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a})
```

## Quick Examples

```markdown
[equation](F = ma)
[equation](A = \pi r^2)
[equation](\sum\_{i=1}^n x_i)
[equation](\int_a^b f(x) dx)
```

## Programmatic Usage

### Using MarkdownBuilder

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Physics Formulas")
    .h2("Mechanics")
    .equation("F = ma")
    .equation("E = \\frac{1}{2}mv^2")
    .h2("Thermodynamics")
    .equation("PV = nRT")
    .h2("Statistics")
    .equation("\\mu = \\frac{1}{n} \\sum_{i=1}^{n} x_i")
)

print(builder.build())
```

## Related Blocks

- **[Code](code.md)** – For computational logic
- **[Table](table.md)** – For organizing formulas
- **[Callout](callout.md)** – For highlighting equations
