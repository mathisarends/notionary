# Connecting to Databases

This guide covers how to connect to existing Notion databases in your workspace using the various factory methods provided by the NotionDatabase class.

## Database Factory Methods

### Connect by Name (Recommended)

The most convenient way to connect to a database is by name using fuzzy matching:

```python
from notionary import NotionDatabase

# Fuzzy name matching - finds closest match
db = await NotionDatabase.from_database_name("Projects")
db = await NotionDatabase.from_database_name("project database")  # Also works
db = await NotionDatabase.from_database_name("proj")  # Partial match
```

The name matching is case-insensitive and handles partial matches, making it easy to find databases without remembering exact titles.

### Connect by Database ID

For precise connections when you know the database ID:

```python
# Using the full database ID
db = await NotionDatabase.from_database_id("12345678-1234-1234-1234-123456789012")

# ID can be found in the database URL or via the Notion API
database_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
db = await NotionDatabase.from_database_id(database_id)
```

### Connect by URL

Connect directly using a Notion database URL:

```python
# From a shared database URL
url = "https://www.notion.so/workspace/database-name-123456789"
db = await NotionDatabase.from_url(url)

# Also works with direct database URLs
internal_url = "https://notion.so/a1b2c3d4e5f678901234567890abcdef"
db = await NotionDatabase.from_url(internal_url)
```

## Workspace Discovery

### List All Databases

Discover all databases in your workspace:

```python
from notionary import NotionWorkspace

workspace = NotionWorkspace()

# Get all accessible databases
databases = await workspace.list_all_databases()

print(f"Found {len(databases)} databases:")
for db in databases:
    print(f"- {db.title} (ID: {db.id})")
    print(f"  URL: {db.url}")
    print(f"  Properties: {len(db.properties)}")
```

### Search for Databases

Find databases by search criteria:

```python
# Search for specific databases
found_databases = await workspace.search_databases("project")

for db in found_databases:
    print(f"Database: {db.title}")
    print(f"Description: {db.description or 'No description'}")
```

## Related Documentation

- **[Database Overview](index.md)** - Core database functionality
- **[Instantiating Pages](instantiating-pages.md)** - Creating pages in databases
- **[Page Management](../page/index.md)** - Working with page content
