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

### Basic Data Table

```markdown
| Name  | Role      | Location |
| ----- | --------- | -------- |
| Alice | Developer | New York |
| Bob   | Designer  | London   |
| Carol | Manager   | Tokyo    |
```

### Pricing Table

```markdown
| Plan       | Price  | Features          | Support   |
| ---------- | ------ | ----------------- | --------- |
| Basic      | $10/mo | Core features     | Email     |
| Pro        | $25/mo | Advanced features | Priority  |
| Enterprise | Custom | All features      | Dedicated |
```

### Status Tracking

```markdown
| Task       | Assignee | Status         | Due Date   |
| ---------- | -------- | -------------- | ---------- |
| API Design | Alice    | ✅ Complete    | 2024-01-15 |
| Frontend   | Bob      | 🔄 In Progress | 2024-01-22 |
| Testing    | Carol    | ⏳ Pending     | 2024-01-29 |
```

## Rich Text in Tables

### Formatted Content

```markdown
| Feature            | Description                      | Priority  |
| ------------------ | -------------------------------- | --------- |
| **Authentication** | User login with _OAuth 2.0_      | 🔴 High   |
| **Database**       | `PostgreSQL` integration         | 🟡 Medium |
| **API**            | REST endpoints with [docs](link) | 🟢 Low    |
```

### Links and References

```markdown
| Resource      | Link                              | Type        |
| ------------- | --------------------------------- | ----------- |
| Documentation | [Docs](https://docs.example.com)  | External    |
| Source Code   | [GitHub](https://github.com/repo) | Repository  |
| Live Demo     | [Demo](https://demo.example.com)  | Application |
```

### Code in Tables

```markdown
| Language   | Example                | Output |
| ---------- | ---------------------- | ------ |
| Python     | `print("Hello")`       | Hello  |
| JavaScript | `console.log("Hello")` | Hello  |
| Bash       | `echo "Hello"`         | Hello  |
```

## Advanced Tables

### Comparison Tables

```markdown
| Feature           | Notionary  | Alternative A | Alternative B |
| ----------------- | ---------- | ------------- | ------------- |
| **Ease of Use**   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐        | ⭐⭐          |
| **Performance**   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐      | ⭐⭐⭐        |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐          | ⭐⭐⭐        |
| **Community**     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐    | ⭐⭐          |
| **Price**         | Free       | $29/mo        | $49/mo        |
```

### Technical Specifications

```markdown
| Component   | Specification   | Notes               |
| ----------- | --------------- | ------------------- |
| **CPU**     | Intel i7-12700K | 8 cores, 16 threads |
| **RAM**     | 32GB DDR4-3200  | Dual channel        |
| **Storage** | 1TB NVMe SSD    | PCIe 4.0            |
| **GPU**     | RTX 4070 Ti     | 12GB VRAM           |
| **PSU**     | 750W 80+ Gold   | Modular cables      |
```

### API Endpoints

```markdown
| Method   | Endpoint          | Description       | Auth Required |
| -------- | ----------------- | ----------------- | ------------- |
| `GET`    | `/api/pages`      | List all pages    | ✅ Yes        |
| `POST`   | `/api/pages`      | Create new page   | ✅ Yes        |
| `GET`    | `/api/pages/{id}` | Get specific page | ✅ Yes        |
| `PATCH`  | `/api/pages/{id}` | Update page       | ✅ Yes        |
| `DELETE` | `/api/pages/{id}` | Delete page       | ✅ Yes        |
```

## Programmatic Usage

### Creating Tables

```python
from notionary.blocks.table import TableMarkdownNode

# Create table programmatically
table = TableMarkdownNode(
    headers=["Name", "Role", "Email"],
    rows=[
        ["Alice Johnson", "Developer", "alice@example.com"],
        ["Bob Smith", "Designer", "bob@example.com"],
        ["Carol Brown", "Manager", "carol@example.com"]
    ]
)

markdown = table.to_markdown()
```

### Dynamic Table Generation

```python
def create_status_table(projects):
    headers = ["Project", "Status", "Progress", "Due Date"]
    rows = []

    for project in projects:
        status_emoji = "✅" if project.completed else "🔄"
        rows.append([
            project.name,
            f"{status_emoji} {project.status}",
            f"{project.progress}%",
            project.due_date.strftime("%Y-%m-%d")
        ])

    return TableMarkdownNode(headers=headers, rows=rows)

# Use with page
table = create_status_table(my_projects)
await page.append_markdown(table.to_markdown())
```

### Data Processing

```python
import csv
from datetime import datetime

async def csv_to_notion_table(csv_file_path, page_name):
    """Convert CSV file to Notion table"""

    # Read CSV data
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        rows = list(reader)

    # Create table
    table = TableMarkdownNode(headers=headers, rows=rows)

    # Add to page
    page = await NotionPage.from_page_name(page_name)
    await page.append_markdown(f"""
# Data Import - {datetime.now().strftime("%Y-%m-%d")}

{table.to_markdown()}
    """)

# Usage
await csv_to_notion_table("sales_data.csv", "Monthly Reports")
```

## Table Formatting

### Alignment (Notion-specific)

While standard Markdown doesn't support alignment in the syntax, Notion tables can be aligned:

```markdown
| Left Aligned | Center Aligned | Right Aligned |
| :----------- | :------------: | ------------: |
| Default      |     Center     |         Right |
| Text         |      Text      |       Numbers |
```

### Column Width Optimization

```markdown
# ✅ Good - Consistent column widths

| Short | Medium Length | Very Long Column Header |
| ----- | ------------- | ----------------------- |
| A     | Data here     | Extended information    |

# ❌ Avoid - Inconsistent widths

| A   | This is a very long header | B   |
| --- | -------------------------- | --- |
| 1   | Short                      | 2   |
```

## Complex Table Examples

### Project Management

```markdown
| 📋 Task        | 👤 Assignee | 📅 Due Date | 🎯 Priority | 📊 Status   | 💬 Notes           |
| -------------- | ----------- | ----------- | ----------- | ----------- | ------------------ |
| API Design     | **Alice**   | 2024-01-15  | 🔴 High     | ✅ Done     | _Review complete_  |
| Frontend Dev   | **Bob**     | 2024-01-22  | 🟡 Medium   | 🔄 Progress | `React components` |
| Database Setup | **Carol**   | 2024-01-20  | 🔴 High     | ⏳ Pending  | PostgreSQL config  |
| Testing        | **David**   | 2024-01-29  | 🟢 Low      | 📝 Planning | Unit + integration |
```

### Financial Reporting

```markdown
| Quarter   | Revenue   | Expenses  | Profit    | Growth   |
| --------- | --------- | --------- | --------- | -------- |
| Q1 2024   | $1.2M     | $800K     | $400K     | +15%     |
| Q2 2024   | $1.4M     | $900K     | $500K     | +17%     |
| Q3 2024   | $1.6M     | $1.0M     | $600K     | +14%     |
| Q4 2024   | $1.8M     | $1.1M     | $700K     | +13%     |
| **Total** | **$6.0M** | **$3.8M** | **$2.2M** | **+15%** |
```

### Feature Comparison

```markdown
| Feature          | Free      | Pro       | Enterprise |
| ---------------- | --------- | --------- | ---------- |
| **Users**        | 3         | 25        | Unlimited  |
| **Storage**      | 5GB       | 100GB     | 1TB        |
| **API Calls**    | 1,000/mo  | 10,000/mo | Unlimited  |
| **Support**      | Community | Email     | 24/7 Phone |
| **Integrations** | Basic     | Advanced  | Custom     |
| **Price**        | $0        | $29/mo    | Contact    |
```

## Best Practices

### Table Design

```markdown
# ✅ Good - Clear headers and consistent data

| Metric  | Current | Target | Status      |
| ------- | ------- | ------ | ----------- |
| Revenue | $1.2M   | $1.5M  | 📈 On track |
| Users   | 5,000   | 7,500  | 📈 Ahead    |
| Churn   | 2.1%    | <2%    | ⚠️ Monitor  |

# ❌ Avoid - Unclear headers and mixed data types

| Thing  | Number       | Stuff | Other  |
| ------ | ------------ | ----- | ------ |
| Sales  | 1.2M dollars | good  | yes/no |
| People | 5000 users   | ok    | true   |
```

### Content Guidelines

- **Keep cells concise** - Long text hurts readability
- **Use consistent formatting** - Same style for similar data
- **Include units** - "$1.2M", "15%", "5 days"
- **Use visual indicators** - ✅❌⚠️🔄📈📉
- **Align data types** - Numbers right, text left

### Performance Considerations

```markdown
# ✅ Good - Reasonable table size

| Name  | Email             | Role   |
| ----- | ----------------- | ------ |
| Alice | alice@example.com | Dev    |
| Bob   | bob@example.com   | Design |

# ⚠️ Large tables - Consider pagination or splitting

# Tables with 50+ rows may impact page performance
```

## Integration with Other Blocks

### Tables with Callouts

```markdown
## Performance Metrics

[callout](📊 **Data as of:** January 2024 "📊")

| KPI     | Value | Change | Target |
| ------- | ----- | ------ | ------ |
| Revenue | $1.2M | +15%   | $1.5M  |
| Users   | 50K   | +22%   | 75K    |

[callout](⚠️ **Note:** Churn rate needs attention "⚠️")
```

### Tables in Toggles

```markdown
+++ Q4 Financial Results
| Month | Revenue | Expenses | Profit |
| ----- | ------- | -------- | ------ |
| October | $400K | $300K | $100K |
| November | $450K | $320K | $130K |
| December | $500K | $350K | $150K |
| **Total** | **$1.35M** | **$970K** | **$380K** |
+++
```

### Tables in Columns

```markdown
::: columns
::: column

## Current Quarter

| Month | Sales |
| ----- | ----- |
| Jan   | $100K |
| Feb   | $120K |
| Mar   | $140K |

:::
::: column

## Last Quarter

| Month | Sales |
| ----- | ----- |
| Oct   | $90K  |
| Nov   | $95K  |
| Dec   | $110K |

:::
:::
```

## Related Blocks

- **[Column](column.md)** - For side-by-side data comparison
- **[Callout](callout.md)** - For highlighting table notes
- **[Code](code.md)** - For formatted data examples
- **[Toggle](toggle.md)** - For collapsible detailed tables
