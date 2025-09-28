# NotionDatabase

The `NotionDatabase` class provides comprehensive functionality for working with Notion databases. Databases are one of Notion's core building blocks, allowing you to store and organize structured data with custom properties, filters, and views.

## Overview

Notion databases combine the flexibility of documents with the structure of spreadsheets. Each database contains pages that act as rows, with properties that define the columns and data types.

For complete information about Notion databases and their capabilities, see the [official Notion API Database reference](https://developers.notion.com/reference/database).

## Core Functionality

### Database Connection

Connect to existing databases using multiple methods:

```python
from notionary import NotionDatabase

# Find by name with fuzzy matching
db = await NotionDatabase.from_database_name("Projects")

# Connect by ID
db = await NotionDatabase.from_database_id("12345678-1234-1234-1234-123456789012")

# Load from URL
db = await NotionDatabase.from_url("https://notion.so/workspace/database-id")
```

### Database Information

Access database metadata and structure:

```python
# Basic information
print(f"Database: {db.title}")
print(f"ID: {db.id}")
print(f"URL: {db.url}")

# Properties and schema
properties = db.properties
for name, config in properties.items():
    print(f"Property: {name} (Type: {config['type']})")
```

### Page Management

Create and manage pages within the database:

```python
# Create new page
page = await db.create_blank_page()
await page.set_title("New Entry")

# Set properties
await page.set_property_value_by_name("Status", "Active")
await page.set_property_value_by_name("Priority", "High")
```

### Querying and Filtering

Query database pages with filters:

```python
# Iterate all pages
async for page in db.iter_pages():
    print(f"Page: {page.title}")

# Filter by criteria
recent_filter = db.create_filter().with_created_last_n_days(7)
async for page in db.iter_pages_with_filter(recent_filter):
    print(f"Recent: {page.title}")
```

## Property Types

Notionary supports all Notion property types including:

- **Text** - Single and multi-line text
- **Number** - Numeric values with formatting
- **Select** - Single choice from predefined options
- **Multi-select** - Multiple choices from options
- **Date** - Dates and date ranges
- **People** - User references
- **Files** - File attachments
- **Checkbox** - Boolean values
- **URL** - Web links
- **Email** - Email addresses
- **Phone** - Phone numbers
- **Formula** - Calculated values
- **Relation** - References to other database pages
- **Rollup** - Aggregate values from relations

## Key Features

### Smart Discovery

Find databases by name without exact matches or complex IDs.

### Property Management

Full support for reading and writing all Notion property types.

### Advanced Filtering

Create complex queries with multiple conditions and date ranges.

### Async Operations

Built for modern Python with full async/await support for optimal performance.

### Type Safety

Comprehensive type hints for better IDE support and code reliability.

## Related Documentation

- **[Instantiating Pages](instantiating-pages.md)** - Create and manage database pages
- **[Page Management](../page/index.md)** - Work with individual pages
- **[Official Notion Database API](https://developers.notion.com/reference/database)** - Complete API reference

## Next Steps

- Learn how to [create and manage pages](instantiating-pages.md) in databases
- Explore [Page Management](../page/index.md) for content operations
- Check the [examples](../examples/) for real-world usage patterns
