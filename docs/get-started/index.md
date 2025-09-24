# Getting Started

Notionary transforms complex Notion API interactions into simple, Pythonic code. Whether you're building AI agents, automating workflows, or creating dynamic content, Notionary makes it effortless.

## Core Features

### Page Management

Work with Notion pages using intuitive Python methods:

```python
from notionary import NotionPage

# Find page by name with fuzzy matching
page = await NotionPage.from_title("Meeting Notes")

# Update content with rich markdown
await page.append_markdown("""
## Action Items
- Review project proposal
- Schedule team meeting
- Update documentation
""")

# Read existing content
content = await page.get_text_content()
print(f"Page content: {content}")
```

### Database Operations

Connect to databases and manage structured data:

```python
from notionary import NotionDatabase

# Connect to database by name
db = await NotionDatabase.from_database_name("Projects")

# Create new entry
page = await db.create_blank_page()
await page.set_title("New Marketing Campaign")
await page.set_property_value_by_name("Status", "Planning")
await page.set_property_value_by_name("Priority", "High")

# Query and filter entries
async for project in db.iter_pages():
    status = await project.get_property_value_by_name("Status")
    print(f"Project: {project.title} - Status: {status}")
```

### Workspace Discovery

Explore and discover content in your Notion workspace:

```python
from notionary import NotionWorkspace

workspace = NotionWorkspace()

# List all databases
databases = await workspace.list_all_databases()
for db in databases:
    print(f"Database: {db.title}")

# Search for pages
pages = await workspace.search_pages("meeting notes", limit=5)
for page in pages:
    print(f"Found: {page.title}")
```

### Rich Markdown Support

Create complex layouts with extended markdown syntax:

```python
# Builder pattern for structured content
await page.replace_content(lambda builder: (
    builder
    .h1("Project Overview")
    .callout("Important project update", "📢")
    .columns(
        lambda col: (col
            .h3("Tasks")
            .bulleted_list(["Design wireframes", "Implement features"])
        ),
        lambda col: (col
            .h3("Timeline")
            .table(
                headers=["Phase", "Due Date"],
                rows=[
                    ["Design", "2024-02-15"],
                    ["Development", "2024-03-31"]
                ]
            )
        )
    )
))

# Or use direct markdown with Notion-specific syntax
await page.append_markdown("""
[callout](Project milestone reached! "🎉")

+++ Additional Details
Advanced configuration and technical specifications
can be found in this collapsible section.
+++
""")
```

## Key Benefits

### Smart Discovery

Find pages and databases by name without remembering exact titles or complex IDs.

### Async-First Architecture

Built for modern Python with full async/await support for optimal performance.

### Roundtrip Compatibility

Read existing content, modify it, and write it back while preserving all formatting.

### Type Safety

Comprehensive type hints for better IDE support and code reliability.

### AI-Ready Integration

Perfect foundation for AI agents that generate and manage Notion content.

## Common Workflows

### Content Automation

```python
# Update project status across multiple pages
async def update_project_status(project_name: str, new_status: str):
    db = await NotionDatabase.from_database_name("Projects")

    async for page in db.iter_pages():
        if project_name in page.title:
            await page.set_property_value_by_name("Status", new_status)
            await page.append_markdown(f"""
            ## Status Update
            Project status changed to: **{new_status}**
            Updated: {datetime.now().strftime('%Y-%m-%d')}
            """)

await update_project_status("Website Redesign", "In Progress")
```

### Documentation Generation

```python
# Generate team documentation automatically
async def create_team_docs():
    page = await NotionPage.from_title("Team Documentation")

    await page.replace_content(lambda builder: (
        builder
        .h1("Team Documentation Hub")
        .callout("Auto-generated team resources", "🤖")
        .h2("Quick Links")
        .bulleted_list([
            "[Project Guidelines](https://wiki.company.com/guidelines)",
            "[Code Standards](https://wiki.company.com/standards)",
            "[Meeting Schedule](https://calendar.company.com/team)"
        ])
        .h2("Current Projects")
        .paragraph("Project status updated automatically:")
    ))

await create_team_docs()
```

## Next Steps

Ready to dive deeper? Explore the comprehensive documentation:

- **[Installation](installation.md)** - Set up your development environment
- **[Page Management](../page/index.md)** - Master page operations and content
- **[Database Operations](../database/index.md)** - Work with structured data
- **[Block Types](../blocks/index.md)** - Complete formatting reference

Start building amazing Notion integrations with Notionary! 🚀
