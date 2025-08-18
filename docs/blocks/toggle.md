# Toggle Blocks

Toggle blocks create collapsible content sections that help organize information and reduce visual clutter. Perfect for FAQ sections, detailed explanations, and progressive disclosure.

## Syntax

```markdown
+++ Toggle Title
Content inside the toggle goes here.
This can be multiple lines and include formatting.
+++
```

## Basic Usage

### Simple Toggle

```markdown
+++ Click to expand
Hidden content goes here.
More details that are initially collapsed.
+++
```

### FAQ Style

```markdown
+++ How do I get started?
1. Create an account
2. Set up your workspace  
3. Invite team members
4. Start building!
+++

+++ What are the pricing options?
We offer three plans:

- **Free**: Up to 3 users
- **Pro**: Unlimited users ($10/month)
- **Enterprise**: Custom pricing
  +++
```

## Rich Content Support

### Formatted Text

```markdown
+++ Advanced Configuration
This toggle contains **important** information about _configuration options_.

You can include `code snippets` and [links](https://example.com).

- Lists work too
- Multiple bullet points
- Nested information
+++
```

### Nested Blocks

````markdown
+++ Development Setup

## Prerequisites

Before starting development:

[callout](💡 **Tip:** Use a virtual environment "💡")

```bash
pip install -r requirements.txt
```
````

### Configuration

Create a `.env` file with:

```
API_TOKEN=your_token_here
```

+++

````

## Programmatic Usage

### Creating Toggles

```python
from notionary.blocks.toggle import ToggleMarkdownNode
from notionary.blocks.paragraph import ParagraphMarkdownNode

# Simple toggle
toggle = ToggleMarkdownNode(
    title="Click to expand",
    children=[
        ParagraphMarkdownNode(text="Hidden content here")
    ]
)

markdown = toggle.to_markdown()
````

### Complex Nested Content

```python
from notionary.blocks.toggle import ToggleMarkdownNode
from notionary.blocks.callout import CalloutMarkdownNode
from notionary.blocks.code import CodeMarkdownNode

# Toggle with multiple child blocks
complex_toggle = ToggleMarkdownNode(
    title="API Integration Guide",
    children=[
        CalloutMarkdownNode(
            text="Ensure you have valid API credentials",
            emoji="🔑"
        ),
        CodeMarkdownNode(
            code="const client = new NotionClient(token);",
            language="javascript"
        )
    ]
)
```

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def add_faq():
    page = await NotionPage.from_page_name("FAQ Page")

    faq_content = """
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
    """

    await page.append_markdown(faq_content)

asyncio.run(add_faq())
```

### With MarkdownBuilder

````python
from notionary.markdown import MarkdownBuilder

def create_documentation():
    builder = MarkdownBuilder()

    builder.heading("API Documentation", level=1)

    # Add toggle sections
    builder.toggle(
        title="Authentication",
        content="""
[callout](🔑 **Required:** API token for all requests "🔑")

```python
headers = {"Authorization": f"Bearer {token}"}
````

        """
    )

    builder.toggle(
        title="Rate Limiting",
        content="Maximum 3 requests per second. Use exponential backoff for retries."
    )

    return builder.build()

await page.replace_content(create_documentation)

````

## Use Cases

### Documentation

```markdown
+++ Installation
```bash
npm install notionary
````

Set up your environment:

```bash
export NOTION_TOKEN="your_token_here"
```

+++

+++ Configuration
Create a `config.json` file:

```json
{
  "apiUrl": "https://api.notion.com/v1",
  "timeout": 5000
}
```

+++

````

### Troubleshooting Guides

```markdown
+++ Error: "Invalid API token"
This error occurs when:
1. Token is expired
2. Token has insufficient permissions
3. Token format is incorrect

**Solution:** Generate a new token in Notion settings.
+++

+++ Error: "Rate limit exceeded"
You're sending requests too quickly.

**Solution:** Implement exponential backoff:
```python
import time
time.sleep(2 ** retry_count)
````

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

+++ Intermediate: Authentication Methods
APIs use various authentication methods:
- **API Keys** - Simple token-based auth
- **OAuth** - Secure delegation
- **JWT** - Stateless tokens
+++
````

## Nested Toggles

````markdown
+++ Development Environment

## Local Setup

+++ Option 1: Docker

```bash
docker run -it notionary/dev
```
````

+++

+++ Option 2: Manual Install

1. Install Python 3.8+
2. Create virtual environment
3. Install dependencies
   +++

## Testing

+++ Unit Tests

```bash
pytest tests/unit/
```

+++

+++ Integration Tests

```bash
pytest tests/integration/
```

+++
+++

```

## Performance Considerations

### Loading Behavior

- Toggles load collapsed by default
- Content is rendered but hidden
- No impact on page load time
- Instant expand/collapse

### SEO and Accessibility

- Content inside toggles is indexed
- Screen readers can access collapsed content
- Keyboard navigation supported
- Semantic HTML structure maintained

## Styling Options

While Notionary focuses on content structure, toggles inherit Notion's visual styling:

- Consistent expand/collapse animations
- Theme-aware colors (light/dark mode)
- Mobile-responsive design
- Icon consistency

## Related Blocks

- **[Toggleable Heading](toggleable-heading.md)** - Collapsible headings
- **[Callout](callout.md)** - Highlighted information boxes
- **[Column](column.md)** - Layout organization
- **[Quote](quote.md)** - Emphasized text blocks
```
