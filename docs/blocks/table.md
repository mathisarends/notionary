# Table Blocks

Table blocks display structured data in rows and columns with support for rich text formatting, sorting, and complex data organization.

## Basic Syntax

```markdown
| Header 1 | Header 2 | Header 3 |
| -------- | -------- | -------- |
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

## Simple Tables

```markdown
| Name  | Role      | Location |
| ----- | --------- | -------- |
| Alice | Developer | New York |
| Bob   | Designer  | London   |
| Carol | Manager   | Tokyo    |
```

### MarkdownBuilder Example

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Team Directory")
    .table(
        headers=["Name", "Role", "Location"],
        rows=[
            ["Alice", "Developer", "New York"],
            ["Bob", "Designer", "London"],
            ["Carol", "Manager", "Tokyo"]
        ]
    )
)

print(builder.build())
```

## Rich Text Content

```markdown
| Feature            | Description                      | Priority  |
| ------------------ | -------------------------------- | --------- |
| **Authentication** | User login with _OAuth 2.0_      | 🔴 High   |
| **Database**       | `PostgreSQL` integration         | 🟡 Medium |
| **API**            | REST endpoints with [docs](link) | 🟢 Low    |
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .h2("Feature Status")
    .table(
        headers=["Feature", "Status", "Priority"],
        rows=[
            ["**Authentication**", "✅ Complete", "🔴 High"],
            ["**Database**", "🔄 In Progress", "🟡 Medium"],
            ["**API**", "📝 Planning", "🟢 Low"]
        ]
    )
)
```

## Comparison Tables

```markdown
| Feature     | Free      | Pro    | Enterprise |
| ----------- | --------- | ------ | ---------- |
| **Users**   | 3         | 25     | Unlimited  |
| **Storage** | 5GB       | 100GB  | 1TB        |
| **Support** | Community | Email  | 24/7 Phone |
| **Price**   | $0        | $29/mo | Contact    |
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .h2("Pricing Plans")
    .table(
        headers=["Feature", "Free", "Pro", "Enterprise"],
        rows=[
            ["**Users**", "3", "25", "Unlimited"],
            ["**Storage**", "5GB", "100GB", "1TB"],
            ["**Support**", "Community", "Email", "24/7 Phone"],
            ["**Price**", "$0", "$29/mo", "Contact"]
        ]
    )
)
```

## API Documentation

```markdown
| Method   | Endpoint          | Description     | Auth Required |
| -------- | ----------------- | --------------- | ------------- |
| `GET`    | `/api/pages`      | List all pages  | ✅ Yes        |
| `POST`   | `/api/pages`      | Create new page | ✅ Yes        |
| `PATCH`  | `/api/pages/{id}` | Update page     | ✅ Yes        |
| `DELETE` | `/api/pages/{id}` | Delete page     | ✅ Yes        |
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .h2("API Endpoints")
    .table(
        headers=["Method", "Endpoint", "Description", "Auth Required"],
        rows=[
            ["`GET`", "`/api/pages`", "List all pages", "✅ Yes"],
            ["`POST`", "`/api/pages`", "Create new page", "✅ Yes"],
            ["`PATCH`", "`/api/pages/{id}`", "Update page", "✅ Yes"],
            ["`DELETE`", "`/api/pages/{id}`", "Delete page", "✅ Yes"]
        ]
    )
)
```

## Status Tracking

```markdown
| Task       | Assignee | Status         | Due Date   |
| ---------- | -------- | -------------- | ---------- |
| API Design | Alice    | ✅ Complete    | 2024-01-15 |
| Frontend   | Bob      | 🔄 In Progress | 2024-01-22 |
| Testing    | Carol    | ⏳ Pending     | 2024-01-29 |
```

### MarkdownBuilder Example

```python
builder = (MarkdownBuilder()
    .h2("Project Status")
    .table(
        headers=["Task", "Assignee", "Status", "Due Date"],
        rows=[
            ["API Design", "Alice", "✅ Complete", "2024-01-15"],
            ["Frontend", "Bob", "🔄 In Progress", "2024-01-22"],
            ["Testing", "Carol", "⏳ Pending", "2024-01-29"]
        ]
    )
)
```

## Best Practices

### Table Design

- Keep headers clear and descriptive
- Use consistent formatting for similar data types
- Include units for numerical values ("$1.2M", "15%", "5 days")
- Use visual indicators (✅❌⚠️🔄📈📉) for status

### Content Guidelines

```markdown
# ✅ Good - Clear headers and consistent data

| Metric  | Current | Target | Status      |
| ------- | ------- | ------ | ----------- |
| Revenue | $1.2M   | $1.5M  | 📈 On track |
| Users   | 5,000   | 7,500  | 📈 Ahead    |

# ❌ Avoid - Unclear headers and mixed data types

| Thing | Number       | Stuff | Other  |
| ----- | ------------ | ----- | ------ |
| Sales | 1.2M dollars | good  | yes/no |
```

### Performance Considerations

- Keep tables under 50 rows for optimal performance
- Consider pagination or splitting for large datasets
- Use consistent column widths

## Integration Examples

### Tables with Callouts

```markdown
[callout](📊 **Data as of:** January 2024 "📊")

| KPI     | Value | Change | Target |
| ------- | ----- | ------ | ------ |
| Revenue | $1.2M | +15%   | $1.5M  |
| Users   | 50K   | +22%   | 75K    |
```

### Tables in Toggles

```markdown
+++ Q4 Financial Results
| Month | Revenue | Expenses | Profit |
| ----- | ------- | -------- | ------ |
| Oct   | $400K   | $300K    | $100K  |
| Nov   | $450K   | $320K    | $130K  |
| Dec   | $500K   | $350K    | $150K  |
+++
```

## Related Blocks

- **[Column](column.md)** - For side-by-side data comparison
- **[Callout](callout.md)** - For highlighting table notes
- **[Code](code.md)** - For formatted data examples
- **[Toggle](toggle.md)** - For collapsible detailed tables
