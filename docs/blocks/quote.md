# Quote

Emphasize a statement or citation. Styled distinct from a paragraph. Supports inline rich text (see [Rich Text](./rich_text.md)) and nested child blocks with indentation.

## Syntax

### Basic Quote
```markdown
> Simplicity is the soul of efficiency.
```

### Multi-line Quote
```markdown
> First line of quote
> Second line of quote
> Third line of quote
```

### Quote with Nested Children
```markdown
> Main quote text
    - Nested list item
    Additional nested content
```

## Examples

### Basic Quotes
```markdown
> The best time to plant a tree was 20 years ago. The second best time is now.
> Code is like humor. When you have to explain it, it's bad. - Cory House
> Follow the **data**, not assumptions.
```

### Quote with Nested Content
```markdown
> Important principle
    - Point one
    - Point two
    See documentation for details
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
