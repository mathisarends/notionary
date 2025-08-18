# Bulleted List Blocks

Bulleted lists organize information in unordered, scannable format. Ideal for features, benefits, or requirements.

## Basic Syntax

```markdown
- First item
- Second item
- Third item
```

## Quick Examples

```markdown
## Features

- Real-time collaboration
- Advanced analytics
- 24/7 support
```

```markdown
## Requirements

- Python 3.8+
- 4GB RAM
- Internet connection
```

```markdown
## Resources

- [Documentation](https://docs.example.com)
- [GitHub Repo](https://github.com/example/repo)
```

## Nested Lists

```markdown
## Project Structure

- Frontend
  - React components
  - CSS styles
- Backend
  - API routes
  - Database models
```

## Mixed Content

```markdown
## API Endpoints

- `GET /api/users` – List users
- `POST /api/users` – Create user
- `PUT /api/users/{id}` – Update user
```

## Programmatic Usage

### Using MarkdownBuilder

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h2("Core Features")
    .bulleted_list([
        "Real-time collaboration",
        "Advanced analytics",
        "Custom integrations"
    ])
    .h2("Resources")
    .bulleted_list([
        "[Docs](https://docs.example.com)",
        "[GitHub](https://github.com/example/repo)"
    ])
)

print(builder.build())
```
