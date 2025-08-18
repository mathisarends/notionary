# Quote Blocks

Quote blocks highlight important text, citations, and emphasized content with visual distinction from regular paragraphs.

## Basic Syntax

```markdown
[quote](This is a quoted text that stands out from regular content)
```

## Quick Examples

```markdown
[quote](The best time to plant a tree was 20 years ago. The second best time is now.)

[quote](Code is like humor. When you have to explain it, it's bad. - Cory House)
```

## Rich Text Formatting

```markdown
[quote](The key to **successful development** is _clean, maintainable code_ that follows established `best practices`.)

[quote](**Rule #1:** Always write code as if the person who ends up maintaining it is a _violent psychopath_ who knows where you live.)

[quote](As documented in our [style guide](https://guide.example.com), consistency is more important than personal preference.)
```

## Programmatic Usage

### Using MarkdownBuilder

```python
from notionary.markdown.markdown_builder import MarkdownBuilder

builder = (MarkdownBuilder()
    .h2("Development Principles")
    .quote("Clean code always looks like it was written by someone who cares. - Michael Feathers")
    .paragraph("This principle guides our coding standards.")
    .quote("Simple is better than complex. Complex is better than complicated.")
    .paragraph("Following the Zen of Python for better design decisions.")
)

print(builder.build())
```

### Creating Quote Blocks Programmatically

```python
from notionary.blocks.quote import QuoteMarkdownNode

# Simple quote
quote = QuoteMarkdownNode(text="Code is poetry written in logic.")

# Rich text quote
rich_quote = QuoteMarkdownNode(
    text="The **best code** is _no code_ at all. Every line is a liability."
)

print(quote.to_markdown())
```

## Common Use Cases

**Important Notes:** Highlight critical information in documentation

**Design Principles:** Emphasize key development philosophies

**Expert Advice:** Share wisdom from industry leaders

**Warnings:** Call attention to important considerations

**Testimonials:** Feature user feedback and success stories

## Best Practices

- Keep quotes concise and impactful
- Use relevant quotes that add value to content
- Avoid overusing quotes in the same section
- Integrate quotes naturally with surrounding content
- Use rich text formatting sparingly for emphasis

## Integration Examples

### With Other Blocks

````markdown
## Security Guidelines

[quote](Always store API tokens securely and never commit them to version control.)

[callout](💡 **Tip:** Use environment variables or secure credential stores.)

```python
import os
token = os.getenv("NOTION_TOKEN")
```
````

````

### In Toggles

```markdown
+++ Development Philosophy
[quote](Simple things should be simple, complex things should be possible. - Alan Kay)

This principle guides our API design decisions and architecture choices.
+++
````

## Reference

Quotes automatically receive visual styling with larger text, left borders, and indentation for clear distinction from regular content.
