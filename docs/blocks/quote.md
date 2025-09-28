# Quote

Emphasize a statement or citation. Styled distinct from a paragraph. Supports inline rich text (see [Rich Text](./rich_text.md)).

## Syntax

```markdown
> Simplicity is the soul of efficiency.
```

## Examples

```markdown
> The best time to plant a tree was 20 years ago. The second best time is now.
> Code is like humor. When you have to explain it, it's bad. - Cory House
> Follow the **data**, not assumptions.
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Principles")
  .quote("Clean code looks like it was written by someone who cares.")
  .paragraph("Guiding standard.")
  .quote("Simple is better than complex.")
  .build())
```
