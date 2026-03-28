# Quickstart

### Create a project and virtual environment

```bash
mkdir my_project
cd my_project
python -m venv .venv
```

### Activate the virtual environment

```bash
source .venv/bin/activate
```

### Install Notionary

```bash
pip install notionary  # or: uv add notionary
```

### Setup Your Notion Integration

#### Step 1: Create a Notion Integration

1. Go to [notion.so/profile/integrations](https://notion.so/profile/integrations)
2. Click **"+ New integration"**
3. Give your integration a name (e.g., "My Notionary App")
4. Select the workspace you want to use
5. Click **"Submit"**

#### Step 2: Get Your Integration Token

After creating the integration, you'll see an **"Internal Integration Token"**. Copy this token.

#### Step 3: Set Environment Variable

Create a `.env` file in your project directory:

```bash
NOTION_API_KEY=your_integration_token_here
```

Or set it directly in your environment:

```bash
export NOTION_API_KEY=your_integration_token_here
```

#### Step 4: Share Pages with Your Integration

Your integration needs access to the pages/databases you want to work with:

1. Open the Notion page or database you want to use
2. Click **"Share"** in the top-right corner
3. Click **"Invite"** and search for your integration name
4. Select your integration and click **"Invite"**

### First Script

```python
import asyncio
from notionary import Notionary

async def main():
    async with Notionary() as notion:
        # List all accessible pages
        pages = await notion.pages.list()
        for page in pages:
            print(f"{page.title} — {page.url}")

        # Find a specific page
        page = await notion.pages.from_title("My Page")

        # Read its content as Markdown
        md = await page.get_markdown()
        print(md)

        # Append new content
        await page.append("## Added by Notionary")

asyncio.run(main())
```
