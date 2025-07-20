# Getting Started

Welcome to Notionary! This guide will get you up and running in just a few minutes.

## Installation

Install Notionary using pip:

```bash
pip install notionary
```

**Requirements:**

- Python 3.8 or higher
- A Notion account with workspace access

## Setup Your Notion Integration

Before using Notionary, you need to create a Notion integration and get your API token.

### Step 1: Create a Notion Integration

1. Go to [notion.so/profile/integrations](https://notion.so/profile/integrations)
2. Click **"+ New integration"**
3. Give your integration a name (e.g., "My Notionary App")
4. Select the workspace you want to use
5. Click **"Submit"**

### Step 2: Get Your Integration Token

After creating the integration, you'll see an **"Internal Integration Token"**. Copy this token - you'll need it next.

### Step 3: Set Environment Variable

Create a `.env` file in your project directory:

```bash
NOTION_SECRET=your_integration_token_here
```

Or set it directly in your environment:

```bash
export NOTION_SECRET=your_integration_token_here
```

### Step 4: Share Pages with Your Integration

Your integration needs access to the pages/databases you want to work with:

1. Open the Notion page or database you want to use
2. Click **"Share"** in the top-right corner
3. Click **"Invite"** and search for your integration name
4. Select your integration and click **"Invite"**

## Your First Notionary Script

Let's create a simple script that updates a Notion page:

```python
import asyncio
from dotenv import load_dotenv
load_dotenv()

from notionary import NotionPage

async def main():
    # Find a page by name (make sure it exists and is shared with your integration)
    page = await NotionPage.from_page_name("My Test Page")

    # Update the page with rich content
    content = """
    # 🚀 Hello from Notionary!

    !> [💡] This content was generated programmatically using Python!

    ## What you can do:
    - Create and update pages
    - Manage database entries
    - Use rich Markdown with custom extensions
    - Build AI-powered content generators

    +++ Click to see more details
    | Notionary makes it incredibly easy to work with Notion's API.
    | No more complex JSON structures - just write Markdown!
    """

    await page.replace_content(content)
    print(f"✅ Page updated successfully!")
    print(f"🔗 View it here: {page.url}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run your script:**

```bash
python your_script.py
```

## Working with Databases

Here's how to work with Notion databases:

```python
import asyncio
from dotenv import load_dotenv
load_dotenv()

from notionary import NotionDatabase

async def main():
    # Connect to a database by name
    db = await NotionDatabase.from_database_name("My Projects")

    # Create a new page in the database
    page = await db.create_blank_page()
    await page.set_title("🆕 New Project")
    await page.set_property_value_by_name("Status", "Planning")

    # Query recent pages
    print("Recent projects:")
    async for i, page in enumerate(db.iter_pages_with_filter(
        db.create_filter().with_created_last_n_days(30)
    ), start=1):
        print(f"{i}. {page.title}")

asyncio.run(main())
```

Happy automating! 🚀
