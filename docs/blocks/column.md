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

## Column Layouts

### Two Column Layout

```markdown
::: columns
::: column

## Features

- Easy to use
- Fast performance
- Great documentation
- Active community
  :::
  ::: column

## Benefits

- Save development time
- Reduce complexity
- Improve maintainability
- Scale efficiently
  :::
  :::
```

### Three Column Layout

```markdown
::: columns
::: column

## Starter

- Basic features
- 1 user
- Email support
- $9/month
  :::
  ::: column

## Professional

- Advanced features
- 10 users
- Priority support
- $29/month
  :::
  ::: column

## Enterprise

- All features
- Unlimited users
- Dedicated support
- Custom pricing
  :::
  :::
```

### Four Column Layout

```markdown
::: columns
::: column

### Q1

Revenue: $1.2M
Growth: +15%
:::
::: column

### Q2

Revenue: $1.4M
Growth: +17%
:::
::: column

### Q3

Revenue: $1.6M
Growth: +14%
:::
::: column

### Q4

Revenue: $1.8M
Growth: +13%
:::
:::
```

## Width Ratios

### Custom Column Widths

```markdown
::: columns
::: column 0.7

## Main Content (70%)

This column takes up 70% of the available width.
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
:::
::: column 0.3

## Sidebar (30%)

This narrower column is perfect for:

- Quick links
- Related info
- Call-to-action
  :::
  :::
```

### Common Ratio Patterns

```markdown
# 2:1 Ratio

::: columns
::: column 0.67
Primary content area
:::
::: column 0.33
Secondary information
:::
:::

# 1:2 Ratio

::: columns
::: column 0.33
Navigation or menu
:::
::: column 0.67
Main article content
:::
:::

# Golden Ratio

::: columns
::: column 0.618
Featured content
:::
::: column 0.382
Supporting details
:::
:::
```

## Rich Content in Columns

### Mixed Content Types

````markdown
::: columns
::: column

## Setup Guide

[callout](💡 **Quick Start:** Follow these steps "💡")

1. Install dependencies
2. Configure settings
3. Run initialization

```bash
npm install
npm run setup
```
````

:::
::: column

## Troubleshooting

+++ Common Issues

- Port already in use
- Missing environment variables
- Permission errors
  +++

+++ Getting Help

- Check documentation
- Join our Discord
- Submit GitHub issue
  +++
  :::
  :::

````

### Code Comparisons

```markdown
::: columns
::: column
### Python Implementation
```python
def fetch_page(page_id):
    response = client.get(f"/pages/{page_id}")
    return response.json()

page = fetch_page("abc123")
print(page["title"])
````

:::
::: column

### JavaScript Implementation

```javascript
async function fetchPage(pageId) {
  const response = await client.get(`/pages/${pageId}`);
  return response.data;
}

const page = await fetchPage("abc123");
console.log(page.title);
```

:::
:::

````

### Before/After Comparisons

```markdown
::: columns
::: column
## ❌ Before
```python
# Manual API calls
import requests

def get_page(page_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=headers)
    return response.json()
````

:::
::: column

## ✅ After

```python
# Using Notionary
from notionary import NotionPage

async def get_page(page_name):
    page = await NotionPage.from_page_name(page_name)
    return page
```

:::
:::

````

## Programmatic Usage

### Creating Column Layouts

```python
from notionary.blocks.column import ColumnListMarkdownNode, ColumnMarkdownNode
from notionary.blocks.paragraph import ParagraphMarkdownNode

# Create columns programmatically
left_column = ColumnMarkdownNode(
    children=[
        ParagraphMarkdownNode(text="Left column content")
    ]
)

right_column = ColumnMarkdownNode(
    children=[
        ParagraphMarkdownNode(text="Right column content")
    ]
)

column_layout = ColumnListMarkdownNode(
    columns=[left_column, right_column]
)

markdown = column_layout.to_markdown()
````

### With Custom Widths

```python
# Custom width ratios
narrow_column = ColumnMarkdownNode(
    children=[...],
    width_ratio=0.3
)

wide_column = ColumnMarkdownNode(
    children=[...],
    width_ratio=0.7
)

layout = ColumnListMarkdownNode(
    columns=[narrow_column, wide_column]
)
```

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def create_comparison():
    page = await NotionPage.from_page_name("Feature Comparison")

    comparison_content = """
# Product Comparison

::: columns
::: column
## Basic Plan
- 5 projects
- 10GB storage
- Email support
- $10/month

[callout](✅ **Best for:** Small teams "✅")
:::
::: column
## Pro Plan
- Unlimited projects
- 100GB storage
- Priority support
- Advanced features
- $25/month

[callout](🚀 **Best for:** Growing companies "🚀")
:::
:::
    """

    await page.replace_content(comparison_content)

asyncio.run(create_comparison())
```

## Layout Patterns

### Documentation Layout

````markdown
::: columns
::: column 0.25

## Navigation

- [Getting Started](#start)
- [API Reference](#api)
- [Examples](#examples)
- [FAQ](#faq)

[callout](💡 **Tip:** Use Cmd+K to search "💡")
:::
::: column 0.75

## Main Content

### Getting Started {#start}

Welcome to our comprehensive documentation.

### Quick Installation

```bash
pip install notionary
```
````

### First Steps

1. Set up authentication
2. Create your first page
3. Add some content
   :::
   :::

````

### Landing Page Layout

```markdown
::: columns
::: column
## Why Choose Us?

### 🚀 Fast Performance
Optimized for speed and efficiency.

### 🔒 Secure by Default
Enterprise-grade security built-in.

### 📚 Great Documentation
Comprehensive guides and examples.

### 🌍 Global Community
Join thousands of developers worldwide.
:::
::: column
## Get Started Today

[callout](🎉 **Free Trial:** No credit card required "🎉")

```bash
# Quick installation
pip install notionary

# Start building
python -c "import notionary; print('Ready!')"
````

### What's Included:

- ✅ Full API access
- ✅ Premium support
- ✅ Advanced features
- ✅ 30-day guarantee

[Start Your Free Trial →](#signup)
:::
:::

````

### Feature Showcase

```markdown
::: columns
::: column 0.4
## Key Features

### 🎯 Focused Design
Clean, intuitive interface that gets out of your way.

### ⚡ Lightning Fast
Optimized performance for large-scale applications.

### 🔧 Highly Configurable
Customize every aspect to fit your workflow.
:::
::: column 0.6
## Live Demo

```python
# See it in action
from notionary import NotionPage

async def demo():
    # Find any page by name
    page = await NotionPage.from_page_name("My Project")

    # Add rich content instantly
    await page.append_markdown("""
    # Project Update

    [callout](✅ **Status:** On track "✅")

    ## Next Steps
    - [ ] Review mockups
    - [ ] Implement features
    - [ ] Deploy to staging
    """)

# Try it yourself!
import asyncio
asyncio.run(demo())
````

:::
:::

````

## Responsive Behavior

### Mobile Considerations

Columns automatically stack on mobile devices:
- **Desktop**: Side-by-side layout
- **Mobile**: Stacked vertically
- **Tablet**: Depends on content width

### Content Guidelines

```markdown
# ✅ Good - Concise content per column
::: columns
::: column
## Short Title
Brief, scannable content works best in columns.
:::
::: column
## Another Title
Keep paragraphs short for better readability.
:::
:::

# ❌ Avoid - Long content in narrow columns
::: columns
::: column
This is a very long paragraph that becomes difficult to read when constrained to a narrow column width. The text becomes choppy and hard to follow.
:::
:::
````

## Nested Layouts

### Columns in Toggles

```markdown
+++ Pricing Comparison
::: columns
::: column
### Basic
$10/month
- Feature A
- Feature B
:::
::: column
### Premium
$25/month  
- All Basic features
- Feature C
- Feature D
:::
:::
+++
```

### Columns in Columns

```markdown
::: columns
::: column

## Left Section

::: columns
::: column

### Sub A

Content A
:::
::: column

### Sub B

Content B
:::
:::
:::
::: column

## Right Section

Full-width content on the right side.
:::
:::
```

## Best Practices

### Content Balance

```markdown
# ✅ Good - Balanced content

::: columns
::: column

## Feature A

Similar amount of content
:::
::: column

## Feature B

Similar amount of content
:::
:::

# ❌ Avoid - Unbalanced content

::: columns
::: column

## Long Section

Very long content that makes this column much taller than the other one.
:::
::: column

## Short

Brief.
:::
:::
```

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

### Accessibility

- Use semantic headings in columns
- Ensure content reads logically when stacked
- Test with screen readers
- Maintain proper contrast ratios

## Related Blocks

- **[Table](table.md)** - For structured data layout
- **[Toggle](toggle.md)** - For collapsible sections in columns
- **[Callout](callout.md)** - For highlighting content in columns
- **[Divider](divider.md)** - For separating column sections
