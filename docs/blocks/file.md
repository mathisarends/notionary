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
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Download Resources")
    .file("https://example.com/user-guide.pdf", "Installation Manual")
    .file("https://releases.example.com/v1.2.0.zip", "Source Code Package")
    .file("https://data.example.com/sample.csv", "Sample Dataset")
)

print(builder.build())
```

## Related Blocks

- **[PDF](pdf.md)** - For inline PDF viewing
- **[Image](image.md)** - For image file display
- **[Video](video.md)** - For video file embeds
- **[Code](code.md)** - For code file examples
