# Divider

Visual break between sections. Simple horizontal rule.

## Syntax

```markdown
---
```

Three or more hyphens on their own line.

## Examples

```markdown
## Section A

Content here.

---

## Section B

More content below the divider.
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Setup")
  .paragraph("Initial steps.")
  .divider()
  .h2("Advanced")
  .paragraph("Complex configuration.")
  .build())
```

## When To Use

- Separate major topics
- Break up long content visually
- Mark transitions between concepts

## Related

- Heading: semantic structure
- Space: blank vertical gap
- Column: layout divisions
