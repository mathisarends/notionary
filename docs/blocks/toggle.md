# Toggle

Collapsible content section with a title. Click to expand/collapse nested blocks.

## Syntax

```markdown
+++ Toggle Title
Content inside toggle.
More paragraphs, lists, etc.
+++
```

## Examples

```markdown
+++ Advanced Configuration
These settings are for power users only.

- Enable debug mode
- Set custom timeouts
- Configure logging
+++
```

Multiple toggles:

```markdown
+++ FAQ: Installation
Download and run the installer.
+++

+++ FAQ: Troubleshooting
Check system requirements first.
+++
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Setup Guide")
  .paragraph("Basic steps.")
  .toggle("Advanced Options", lambda t:
    t.paragraph("Power user settings.")
    .bulleted_list(["Debug mode", "Custom timeouts"])
  )
  .build())
```
