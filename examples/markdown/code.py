"""
# Notionary: CodeBlock Element Markdown Demo
============================================

A demo showing how to add custom code block elements to Notion pages using Markdown.
Perfect for demonstrating CodeBlockElement syntax!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demo of adding CodeBlockElement markdown to a Notion page."""

    print("🚀 Notionary CodeBlock Element Demo")
    print("=" * 38)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        codeblock_content = """
        ## 💻 CodeBlock Element Examples

        ```python
        def hello_world():
            print("Hello, Notionary!")
            return "Success"
        ```
        Caption: Basic Python function example

        ```json
        {
            "name": "Alice",
            "age": 30,
            "skills": ["Python", "JavaScript", "Notion"]
        }
        ```
        Caption: User data structure

        ```bash
        git add .
        git commit -m "Add new features"
        git push origin main
        ```
        Caption: Git workflow commands

        ```javascript
        const fetchData = async () => {
            const response = await fetch('/api/data');
            return response.json();
        };
        ```

        ```mermaid
        erDiagram
            WORKSPACE {
                string workspace_id PK
                string name
                string domain
                datetime created_at
                string plan_type
                boolean is_public
            }
            
            USER {
                string user_id PK
                string email
                string name
                string avatar_url
                string role
                datetime last_active
            }
            
            DATABASE {
                string database_id PK
                string workspace_id FK
                string created_by FK
                string title
                string description
                json properties_schema
                datetime created_at
                datetime last_edited
                string cover_url
                string emoji
            }
            
            PAGE {
                string page_id PK
                string workspace_id FK
                string database_id FK
                string parent_page_id FK
                string created_by FK
                string title
                json content_blocks
                json properties
                datetime created_at
                datetime last_edited
                string cover_url
                string emoji
                boolean is_archived
            }
            
            PERMISSION {
                string permission_id PK
                string user_id FK
                string resource_id
                string resource_type
                string access_level
                datetime granted_at
            }
            
            WORKSPACE ||--o{ USER : "has members"
            WORKSPACE ||--o{ DATABASE : "contains"
            WORKSPACE ||--o{ PAGE : "contains"
            USER ||--o{ DATABASE : "creates"
            USER ||--o{ PAGE : "creates"
            USER ||--o{ PERMISSION : "has"
            DATABASE ||--o{ PAGE : "contains entries"
            PAGE ||--o{ PAGE : "has subpages"
            DATABASE ||--|| USER : "created by"
            PAGE ||--|| USER : "created by"
            PAGE }o--|| DATABASE : "belongs to"
            PAGE }o--|| PAGE : "child of"
        ```
        Caption: Notion workspace entity relationship diagram
        """

        # Add the markdown content to the page
        print("\n📝 Adding CodeBlock Element examples...")
        await page.append_markdown(codeblock_content)

        print(f"\n✅ Successfully added codeblock examples to '{page.title}'!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
