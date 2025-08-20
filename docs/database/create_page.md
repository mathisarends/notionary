# Create a Page in a Database

This guide walks through the complete process of creating pages in Notion databases, from basic page creation to advanced workflows with content and property management.

## Basic Page Creation

When you use `create_blank_page`, it returns a `NotionPage` instance. This means you can immediately access all available methods for that page, such as updating properties or reading and writing its content.

Creating a page in a database involves connecting to the database, creating the page, and then using the page instance to set properties or manage content:

```python
from notionary import NotionDatabase

# Step 1: Connect to your database
db = await NotionDatabase.from_database_name("Projects")

# Step 2: Create a blank page (returns a NotionPage instance)
page = await db.create_blank_page()

# Step 3: Set the page title
await page.set_title("New Marketing Campaign")

# Step 4: Set essential properties
await page.set_property_value_by_name("Status", "Planning")
await page.set_property_value_by_name("Priority", "High")

# Step 5: Add or read page content as needed
await page.append_markdown("Kickoff scheduled for next week.")
content = await page.read_content()
```

### Immediate Property Setting

Set multiple properties right after creation:

```python
# Create page and set properties immediately
page = await db.create_blank_page()
await page.set_title("Q1 Product Launch")

# Configure all essential properties
await page.set_property_value_by_name("Status", "In Progress")
await page.set_property_value_by_name("Priority", "High")
await page.set_property_value_by_name("Team Lead", "sarah@company.com")
await page.set_property_value_by_name("Budget", 150000)
await page.set_property_value_by_name("Due Date", "2024-03-31")
await page.set_property_value_by_name("Tags", ["product", "marketing", "launch"])
```

## Related Documentation

- **[Database Overview](index.md)** - Core database functionality
- **[Connecting to Databases](connecting.md)** - How to connect to databases
- **[Page Management](../page/index.md)** - Working with page content
