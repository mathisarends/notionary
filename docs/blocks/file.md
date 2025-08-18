# File Blocks

File blocks provide downloadable attachments and file links for documents, archives, and other resources.

## Syntax

```markdown
[file](https://example.com/document.pdf)
[file](https://example.com/archive.zip "Project Files")
```

## Supported File Types

### Documents

```markdown
[file](https://docs.example.com/user-guide.pdf "User Guide")
[file](https://files.example.com/api-spec.docx "API Specification")
[file](https://assets.example.com/presentation.pptx "Product Demo")
```

### Archives

```markdown
[file](https://downloads.example.com/source-code.zip "Source Code")
[file](https://releases.example.com/v1.2.0.tar.gz "Release Package")
```

### Data Files

```markdown
[file](https://data.example.com/sample-data.csv "Sample Dataset")
[file](https://exports.example.com/report.xlsx "Monthly Report")
[file](https://backups.example.com/database.sql "Database Backup")
```

## Programmatic Usage

```python
from notionary.blocks.file import FileMarkdownNode

# File with caption
file_block = FileMarkdownNode(
    url="https://example.com/manual.pdf",
    caption="Installation Manual"
)

# Add to documentation
await page.append_markdown('[file](https://example.com/guide.pdf "Setup Guide")')
```

## File Information

Files display:

- **File name** from URL or caption
- **File size** (when available)
- **File type icon** based on extension
- **Download link** for direct access

## Common File Types

- **PDF** - Documents, manuals, reports
- **ZIP/TAR** - Source code, assets, packages
- **CSV/XLSX** - Data exports, spreadsheets
- **DOC/DOCX** - Text documents, specifications
- **JSON/XML** - Configuration, data files

## Best Practices

- **Descriptive captions**: Clearly describe file contents
- **File organization**: Group related files together
- **Version control**: Include version numbers in names
- **Access permissions**: Ensure files are publicly accessible

## Common Use Cases

- **Documentation attachments** - Supplementary materials
- **Software releases** - Download packages
- **Data exports** - CSV reports and datasets
- **Templates** - Downloadable examples
- **Resources** - Additional materials

## Related Blocks

- **[PDF](pdf.md)** - For inline PDF viewing
- **[Image](image.md)** - For image file display
- **[Video](video.md)** - For video file embeds
- **[Code](code.md)** - For code file examples
