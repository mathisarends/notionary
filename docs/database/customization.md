# Database Customization

This guide covers how to customize the appearance and metadata of Notion databases, including titles, emojis, cover images, and icons.

## Update Database Title

Change the display name of your database:

```python
from notionary import NotionDatabase

# Connect to database
db = await NotionDatabase.from_database_name("Old Project Name")

# Update the title
success = await db.set_title("New Project Database")

if success:
    print(f"Database title updated to: {db.title}")
else:
    print("Failed to update database title")
```

## Set Database Emoji

Add or change the emoji icon for your database:

```python
# Set a project-related emoji
success = await db.set_emoji("🚀")

# Set different emojis for different types of databases
await db.set_emoji("📋")  # For task databases
await db.set_emoji("👥")  # For team databases
await db.set_emoji("📊")  # For analytics databases
await db.set_emoji("💼")  # For business databases

if success:
    print(f"Database emoji updated to: {db.emoji_icon}")
```

### Thematic Emoji Examples

Choose emojis that match your database purpose:

```python
# Project management
await db.set_emoji("🎯")  # Goals and objectives
await db.set_emoji("⚡")  # Fast-moving projects
await db.set_emoji("🏗️")  # Construction/building projects

# Content management
await db.set_emoji("📝")  # Documentation
await db.set_emoji("📚")  # Knowledge base
await db.set_emoji("🎨")  # Creative projects

# Business operations
await db.set_emoji("💰")  # Financial tracking
await db.set_emoji("📈")  # Analytics and metrics
await db.set_emoji("🔧")  # Operations and maintenance
```

## External Icon URL

Use custom images as database icons:

```python
# Set custom icon from URL
icon_url = await db.set_external_icon("https://example.com/project-icon.png")

if icon_url:
    print(f"Database icon updated: {icon_url}")
else:
    print("Failed to set external icon")
```

## Database Cover Images

Set a custom cover image for your database:

```python
# Set custom cover from URL
cover_url = await db.set_cover_image("https://example.com/project-banner.jpg")

if cover_url:
    print(f"Database cover updated: {cover_url}")
else:
    print("Failed to set cover image")
```

### Random Gradient Cover

Use Notion's built-in gradient covers:

```python
# Set a random gradient cover
gradient_url = await db.set_random_gradient_cover()

if gradient_url:
    print(f"Random gradient cover applied: {gradient_url}")
```

## Related Documentation

- **[Database Overview](index.md)** - Core database functionality
- **[Connecting to Databases](connecting.md)** - How to connect to databases
- **[Create a Page](create_page.md)** - Creating pages in databases
