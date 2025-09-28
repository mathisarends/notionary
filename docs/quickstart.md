### Create a project and virtual environemnt

You'll only need to do this once.

```bash
mkdir my_project
cd my_project
python -m venv .venv
```

### Activate the virtual environment

Do this every time you start a new terminal session.

```bash
source .venv/bin/activate
```

### Install Notionary

```bash
pip install notionary # or uv add notionary etc.
```

### Setup Your Notion Integration

Before using Notionary, you need to create a Notion integration and get your API token.

#### Step 1: Create a Notion Integration

1. Go to [notion.so/profile/integrations](https://notion.so/profile/integrations)
2. Click **"+ New integration"**
3. Give your integration a name (e.g., "My Notionary App")
4. Select the workspace you want to use
5. Click **"Submit"**

#### Step 2: Get Your Integration Token

After creating the integration, you'll see an **"Internal Integration Token"**. Copy this token - you'll need it next.

#### Step 3: Set Environment Variable

Create a `.env` file in your project directory:

```bash
NOTION_SECRET=your_integration_token_here
```

Or set it directly in your environment:

```bash
export NOTION_SECRET=your_integration_token_here
```

#### Step 4: Share Pages with Your Integration

Your integration needs access to the pages/databases you want to work with:

1. Open the Notion page or database you want to use
2. Click **"Share"** in the top-right corner
3. Click **"Invite"** and search for your integration name
4. Select your integration and click **"Invite"**
