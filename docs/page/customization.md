# Page Customization

This guide covers how to customize the appearance, metadata, and properties of Notion pages.

## Page Title

Update the page title:

```python
from notionary import NotionPage

page = await NotionPage.from_title("Old Title")
title = await page.set_title("New Page Title")
```

## Page Icons

Set the page emoji icon:

```python
# Set emoji
emoji = await page.set_emoji_icon("🚀")

# Different options
await page.set_emoji_icon("📝")  # Document
await page.set_emoji_icon("📋")  # Task
await page.set_emoji_icon("🎯")  # Goal
```

### External Icon

Use custom images as page icons:

```python
icon_url = await page.set_external_icon("https://example.com/icon.png")
```

## Cover Images

Set a custom cover image from any URL:

```python
cover_url = await page.set_cover("https://example.com/banner.jpg")

# Use company branding
company_banner = "https://company.com/assets/page-header.jpg"
await page.set_cover(company_banner)

# Project-specific covers
project_cover = "https://assets.example.com/project-banner.png"
await page.set_cover(project_cover)
```

### Random Gradient Cover

Use Notion's built-in gradient covers:

```python
gradient_url = await page.set_random_gradient_cover()

# Creates a random gradient from Notion's default options
# Returns URL like: https://www.notion.so/images/page-cover/gradients_3.png
```

### Get Current Cover

Retrieve the current cover URL:

```python
current_cover = await page.get_cover_url()

if current_cover:
    print(f"Current cover: {current_cover}")
else:
    print("No cover image set")
```

## Database Properties

For pages within databases, manage custom properties:

### Read Properties

Get property values from database pages:

```python
# Get individual properties
status = await page.get_property_value_by_name("Status")
priority = await page.get_property_value_by_name("Priority")
due_date = await page.get_property_value_by_name("Due Date")
tags = await page.get_property_value_by_name("Tags")

print(f"Status: {status}")
print(f"Priority: {priority}")
print(f"Due: {due_date}")
print(f"Tags: {tags}")
```

### Update Properties

Set property values on database pages:

```python
# Text and select properties
await page.set_property_value_by_name("Status", "In Progress")
await page.set_property_value_by_name("Priority", "High")

# Number and date properties
await page.set_property_value_by_name("Budget", 50000)
await page.set_property_value_by_name("Due Date", "2024-03-15")

# Checkbox properties
await page.set_property_value_by_name("Approved", True)

# Multi-select properties
await page.set_property_value_by_name("Tags", ["urgent", "client-work"])

# URL and email properties
await page.set_property_value_by_name("Repository", "https://github.com/user/repo")
await page.set_property_value_by_name("Contact", "user@example.com")
```

### Relation Properties

Link pages to other database entries:

```python
# Set related pages by title
related_pages = ["Project Alpha", "Project Beta"]
await page.set_relation_property_values_by_name("Dependencies", related_pages)

# Get related page titles
dependencies = await page.get_property_value_by_name("Dependencies")
print(f"Related projects: {dependencies}")
```

### Property Options

Get available options for select properties:

```python
# Get valid options before setting
status_options = await page.get_options_for_property_by_name("Status")
priority_options = await page.get_options_for_property_by_name("Priority")

print(f"Available statuses: {status_options}")
print(f"Available priorities: {priority_options}")

# Set using valid option
if "In Review" in status_options:
    await page.set_property_value_by_name("Status", "In Review")
```

## Complete Setup

Apply comprehensive customization:

```python
# Full page customization workflow
page = await NotionPage.from_title("My Project")

# Update appearance
await page.set_title("🚀 Project Alpha - Complete Guide")
await page.set_emoji_icon("🚀")
await page.set_cover("https://company.com/project-banner.jpg")

# Update database properties (if page is in database)
await page.set_property_value_by_name("Status", "Active")
await page.set_property_value_by_name("Priority", "High")
await page.set_property_value_by_name("Due Date", "2024-03-31")
await page.set_property_value_by_name("Team Lead", "manager@company.com")

print(f"Page customized: {page.url}")
```

## Related Documentation

- **[Page Overview](index.md)** - Core page functionality
- **[Content Management](content.md)** - Managing page content
- **[Property Management](properties.md)** - Advanced property operations
