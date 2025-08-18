# Column Blocks

Column blocks enable multi-column layouts for organizing content side-by-side. Perfect for comparisons, feature lists, and responsive design patterns.

## Basic Syntax

```markdown
::: columns
::: column
Left column content
:::
::: column  
Right column content
:::
:::
```

### MarkdownBuilder Example

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Product Comparison")
    .columns(
        lambda col: col.h3("Features").bulleted_list(["Fast", "Secure", "Reliable"]),
        lambda col: col.h3("Benefits").bulleted_list(["Save time", "Reduce costs", "Scale easily"])
    )
)

print(builder.build())
```

## Column Layouts

### Multiple Columns

```markdown
::: columns
::: column

## Starter

- Basic features
- $9/month
  :::
  ::: column

## Professional

- Advanced features
- $29/month
  :::
  ::: column

## Enterprise

- All features
- Custom pricing
  :::
  :::
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .h2("Pricing Plans")
    .columns(
        lambda col: col.h3("Starter").bulleted_list(["Basic features", "$9/month"]),
        lambda col: col.h3("Professional").bulleted_list(["Advanced features", "$29/month"]),
        lambda col: col.h3("Enterprise").bulleted_list(["All features", "Custom pricing"])
    )
)
```

## Width Ratios

### Custom Column Widths

```markdown
::: columns
::: column 0.7

## Main Content (70%)

Primary content area with more space.
:::
::: column 0.3

## Sidebar (30%)

- Quick links
- Related info
  :::
  :::
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .h1("Documentation Layout")
    .columns(
        lambda col: col.h2("Main Content").paragraph("Primary content area"),
        lambda col: col.h3("Sidebar").bulleted_list(["Quick links", "Related info"]),
        width_ratios=[0.7, 0.3]
    )
)
```

## Rich Content

### Mixed Content Types

````markdown
::: columns
::: column

## Setup Guide

[callout](💡 **Quick Start:** Follow these steps "💡")

```bash
pip install notionary
```

:::
::: column

## Troubleshooting

+++ Common Issues

- Port already in use
- Missing variables
  +++
  :::
  :::
````

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .columns(
        lambda col: (col
            .h2("Setup Guide")
            .callout("💡 **Quick Start:** Follow these steps", "💡")
            .code("pip install notionary", "bash")
        ),
        lambda col: (col
            .h2("Troubleshooting")
            .toggle("Common Issues", lambda t: t.bulleted_list([
                "Port already in use",
                "Missing variables"
            ]))
        )
    )
)
```

## Code Comparisons

### Before/After Example

````markdown
::: columns
::: column

## ❌ Before

```python
import requests
response = requests.get(url, headers=headers)
data = response.json()
```

:::
::: column

## ✅ After

```python
from notionary import NotionPage
page = await NotionPage.from_page_name("My Page")
```

:::
:::
````

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .h2("API Comparison")
    .columns(
        lambda col: (col
            .h3("❌ Before")
            .code('import requests\nresponse = requests.get(url)', "python")
        ),
        lambda col: (col
            .h3("✅ After")
            .code('from notionary import NotionPage\npage = await NotionPage.from_page_name("My Page")', "python")
        )
    )
)
```

## Nested Layouts

### Columns in Toggles

```markdown
+++ Pricing Comparison
::: columns
::: column
### Basic
$10/month
:::
::: column
### Premium  
$25/month
:::
:::
+++
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .toggle("Pricing Comparison", lambda t: t.columns(
        lambda col: col.h3("Basic").paragraph("$10/month"),
        lambda col: col.h3("Premium").paragraph("$25/month")
    ))
)
```

## Responsive Behavior

Columns automatically stack on mobile devices:

- **Desktop**: Side-by-side layout
- **Mobile**: Stacked vertically
- **Tablet**: Depends on content width

### Content Guidelines

```markdown
# ✅ Good - Concise content

::: columns
::: column

## Short Title

Brief, scannable content works best.
:::
::: column

## Another Title

Keep paragraphs short for readability.
:::
:::
```

## Best Practices

### Content Balance

- Keep similar content amounts in each column
- Use semantic headings for accessibility
- Test with screen readers
- Ensure content reads logically when stacked

### Visual Hierarchy

```markdown
::: columns
::: column

## Primary Focus

### Important Details

Key information here.
:::
::: column

## Secondary Info

### Supporting Details

Additional context.
:::
:::
```

## Related Blocks

- **[Table](table.md)** - For structured data layout
- **[Toggle](toggle.md)** - For collapsible sections in columns
- **[Callout](callout.md)** - For highlighting content in columns
- **[Divider](divider.md)** - For separating column sections
