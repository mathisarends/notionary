# Equation

Block‑level LaTeX mathematical expressions.

## Syntax

```markdown
$$E = mc^2$$
```

Multi‑line:

```markdown
$$
x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}
$$
```

## Examples

```markdown
$$\sum_{i=1}^{n} x_i = x_1 + x_2 + \ldots + x_n$$

$$\int_{a}^{b} f(x) dx = F(b) - F(a)$$
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Physics Formulas")
  .equation("E = mc^2")
  .paragraph("Einstein's mass‑energy equivalence.")
  .equation("F = ma")
  .build())
```

!!! info "Notion API Reference"
    For the official Notion API reference on equation blocks, see <a href="https://developers.notion.com/reference/block#equation" target="_blank">https://developers.notion.com/reference/block#equation</a>
