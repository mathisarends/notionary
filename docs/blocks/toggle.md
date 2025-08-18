# Toggle Blocks

Toggle blocks create collapsible content sections that help organize information and reduce visual clutter. Perfect for FAQ sections, detailed explanations, and progressive disclosure.

## Basic Syntax

```markdown
+++ Toggle Title
Content inside the toggle goes here.
This can be multiple lines and include formatting.
+++
```

## Simple Toggle

```markdown
+++ Click to expand
Hidden content goes here.
More details that are initially collapsed.
+++
```

### MarkdownBuilder Example

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("FAQ Page")
    .toggle("How do I get started?", lambda content: (content
        .numbered_list([
            "Create an account",
            "Set up your workspace",
            "Invite team members",
            "Start building!"
        ])
    ))
)

print(builder.build())
```

## Rich Content

````markdown
+++ Advanced Configuration
This toggle contains **important** information about _configuration options_.

You can include `code snippets` and [links](https://example.com).

```bash
pip install notionary
```
````

+++

````

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .toggle("Development Setup", lambda content: (content
        .h2("Prerequisites")
        .callout("💡 **Tip:** Use a virtual environment", "💡")
        .code("pip install -r requirements.txt", "bash")
        .paragraph("Create a `.env` file with your API token.")
    ))
)
````

## Nested Content

```markdown
+++ Documentation Guide
## Installation

[callout](💡 **Quick Start:** Follow these steps "💡")

1. Install dependencies
2. Configure settings
3. Run initialization

+++ Troubleshooting
- Port already in use
- Missing environment variables
- Permission errors
+++

+++
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .toggle("API Documentation", lambda content: (content
        .toggle("Authentication", lambda auth: (auth
            .callout("🔑 **Required:** API token for all requests", "🔑")
            .code('headers = {"Authorization": f"Bearer {token}"}', "python")
        ))
        .toggle("Rate Limiting", lambda rate: (rate
            .paragraph("Maximum 3 requests per second.")
            .code("time.sleep(2 ** attempt)", "python", "Exponential backoff")
        ))
    ))
)
```

## Use Cases

### FAQ Sections

```markdown
+++ How do I reset my password?
1. Go to the login page
2. Click "Forgot Password"
3. Check your email for reset link
4. Follow the instructions
+++

+++ Can I export my data?
Yes! You can export your data in several formats:

- **JSON** - Complete data export
- **CSV** - Spreadsheet format
- **PDF** - Printable documents
  +++
```

### Documentation

````markdown
+++ Installation

```bash
pip install notionary
```
````

Set up your environment:

```bash
export NOTION_TOKEN="your_token_here"
```

+++

````

### Learning Materials

```markdown
+++ Beginner: What is an API?
An API (Application Programming Interface) is a way for different
software applications to communicate with each other.

Think of it like a waiter in a restaurant - you give your order
(request) to the waiter, who takes it to the kitchen (server),
and brings back your food (response).
+++
````

## Related Blocks

- **[Toggleable Heading](toggleable-heading.md)** - Collapsible headings
- **[Callout](callout.md)** - Highlighted information boxes
- **[Column](column.md)** - Layout organization
- **[Quote](quote.md)** - Emphasized text blocks
