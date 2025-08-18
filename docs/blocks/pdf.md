# PDF Blocks

PDF blocks embed PDF documents directly in pages for inline viewing without requiring downloads.

## Syntax

```markdown
[pdf](https://example.com/document.pdf)
[pdf](https://example.com/manual.pdf "Installation Manual")
```

## Basic Usage

### Documentation

```markdown
## User Manual

[pdf](https://docs.example.com/user-manual.pdf "Complete User Manual")

## API Reference

[pdf](https://api.example.com/reference.pdf "API Documentation")
```

### Reports

```markdown
## Monthly Analytics

[pdf](https://reports.example.com/analytics-march.pdf "March 2024 Report")

## Financial Summary

[pdf](https://finance.example.com/q1-summary.pdf "Q1 Financial Report")
```

## Programmatic Usage

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Documentation Library")
    .pdf("https://docs.example.com/user-manual.pdf", "Complete User Manual")
    .pdf("https://api.example.com/reference.pdf", "API Documentation")
    .pdf("https://reports.example.com/analytics.pdf", "Monthly Analytics Report")
)

print(builder.build())
```

## Related Blocks

- **[File](file.md)** - For downloadable PDF files
- **[Image](image.md)** - For PDF page screenshots
- **[Embed](embed.md)** - For other document types
- **[Bookmark](bookmark.md)** - For PDF preview links
