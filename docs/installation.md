# Installation

Get Notionary up and running in just a few steps.

## Requirements

- **Python 3.8 or higher**
- **A Notion account** with workspace access

## Install Notionary

Install using pip:

```bash
pip install notionary
```

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

## Verify Installation

Test your setup with a simple script:

```python
import asyncio
from dotenv import load_dotenv
load_dotenv()

from notionary import NotionWorkspace

async def test_connection():
    workspace = NotionWorkspace()
    try:
        databases = await workspace.list_all_databases()
        print(f"✅ Connected! Found {len(databases)} databases.")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
```

If you see the success message, you're ready to start using Notionary!

## Next Steps

- **[Getting Started](index.md)** - Learn what Notionary can do and see examples
- **[Page Management](../page/index.md)** - Work with individual Notion pages
- **[Database Operations](../database/index.md)** - Query and manage databases
- **[Examples](../../examples/)** - Real-world usage examples
