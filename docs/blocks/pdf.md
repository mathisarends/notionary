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
from notionary.blocks.pdf import PdfMarkdownNode

# PDF with caption
pdf_block = PdfMarkdownNode(
    url="https://example.com/guide.pdf",
    caption="Setup Guide"
)

# Add to page
await page.append_markdown('[pdf](https://docs.example.com/manual.pdf "User Manual")')
```

## Viewer Features

PDF embeds provide:

- **Inline viewing** - No download required
- **Page navigation** - Browse through document
- **Zoom controls** - Adjust viewing size
- **Search** - Find text within PDF
- **Download option** - Save local copy

## Supported Sources

- **External URLs** - Publicly accessible PDFs
- **CDN links** - Content delivery networks
- **Cloud storage** - Google Drive, Dropbox (public links)
- **Documentation sites** - Direct PDF links

## Best Practices

- **File size**: Keep PDFs under 10MB for best performance
- **Public access**: Ensure PDFs are publicly accessible
- **Descriptive captions**: Explain PDF contents
- **Mobile consideration**: PDFs may be less readable on mobile

## Common Use Cases

- **User manuals** - Product documentation
- **Technical specs** - Detailed specifications
- **Reports** - Data analysis and summaries
- **Forms** - Fillable documents
- **Presentations** - Slide decks and pitches

## Related Blocks

- **[File](file.md)** - For downloadable PDF files
- **[Image](image.md)** - For PDF page screenshots
- **[Embed](embed.md)** - For other document types
- **[Bookmark](bookmark.md)** - For PDF preview links
