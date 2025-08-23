# Mentions

Mentions create automatic links to pages, databases, and users in your Notion workspace. They provide dynamic connectivity and keep your content up-to-date when referenced items change.

## Overview

Mentions automatically resolve names to IDs and create clickable links in your Notion workspace. When mentioned items are renamed, the mentions update automatically to reflect the changes.

**Key Features:**

- Use either human-readable names or direct IDs
- All mentions convert to readable names in markdown output
- Names are automatically resolved to current titles

## User Mentions

Reference team members and collaborators in your workspace.

### Syntax

```markdown
@user[User Name]
@user[user-id-here]
@user[email@company.com]
```

### Examples

```markdown
Please review this with @user[Sarah Johnson] before Friday.
Ask @user[john@company.com] about the deployment process.
The project lead is @user[Alex Chen] - reach out with questions.
```

### User Resolution

- **By Name:** Searches workspace members for closest name match
- **By Email:** Exact email address match in workspace
- **By ID:** Direct Notion user ID reference
- **Fallback:** If user not found, displays as plain text

## Page Mentions

Link to other pages in your workspace for cross-referencing and navigation.

### Syntax

```markdown
@page[Page Title]
@page[page-id-here]
```

### Examples

```markdown
See the detailed timeline in @page[Q4 Product Roadmap].
Update the information in @page[Team Onboarding Guide].
Requirements are documented in @page[API Specification].
```

### Page Resolution

- **By Title:** Fuzzy matching against page titles workspace-wide
- **By ID:** Direct Notion page ID reference
- **Auto-Update:** Page mentions update when referenced pages are renamed
- **Fallback:** If page not found or inaccessible, displays as plain text

## Database Mentions

Reference databases for data organization and workflow connections.

### Syntax

```markdown
@database[Database Name]  
@database[database-id-here]
```

### Examples

```markdown
Add new entries to @database[Customer Feedback].
Check the status in @database[Project Tasks].
All team information is stored in @database[Employee Directory].
```

### Database Resolution

- **By Title:** Fuzzy matching against database titles
- **By ID:** Direct Notion database ID reference
- **Auto-Update:** Database mentions update when databases are renamed
- **Fallback:** If database not found or inaccessible, displays as plain text

## Advanced Usage

### Mentions with Formatting

Combine mentions with rich text formatting:

```markdown
**Important:** @user[Project Manager] needs to approve @page[Budget Proposal]
_Note:_ Check @database[Tasks] for **urgent** items
~~Old process~~: See updated workflow in @page[New Procedures]
```

### Mentions in Different Blocks

**In Callouts:**

```markdown
[callout](@user[Sarah]: Please review the changes in @page[Design System] "📝")
```

**In Lists:**

```markdown
- @user[John] - Handle @database[Customer Issues]
- @user[Alice] - Update @page[Documentation]
- @user[Bob] - Review @page[Code Guidelines]
```

**In Tables:**

```markdown
| Task           | Owner        | Reference                |
| -------------- | ------------ | ------------------------ |
| Design Review  | @user[Sarah] | @page[UI Mockups]        |
| Database Setup | @user[Mike]  | @database[User Accounts] |
```

**In Toggles:**

```markdown
+++Project Details
Main contact: @user[Project Lead]
Documentation: @page[Project Overview]
Task tracking: @database[Sprint Tasks]
+++
```

## Permissions and Access

### Workspace Visibility

- Mentions only resolve within your current Notion workspace
- Users must have access to mentioned pages/databases to see content
- Mentions respect existing Notion permission settings

### Access Levels

- **Full Access:** Mention displays as clickable link
- **Limited Access:** Mention displays with restricted styling
- **No Access:** Mention displays as plain text
- **Not Found:** Mention displays as plain text with original syntax

## Best Practices

### Naming Conventions

Use consistent, descriptive names for better mention resolution:

```markdown
✅ Clear and specific
@page[Q4 Marketing Campaign Plan]
@database[Customer Support Tickets]
@user[Sarah Johnson - Design Lead]

❌ Vague or ambiguous  
@page[Plan]
@database[Stuff]
@user[Sarah]
```

### Context and Clarity

Provide context around mentions for better readability:

```markdown
✅ Good context
The project timeline is detailed in @page[Q4 Development Schedule].
Please coordinate with @user[Project Manager] for any changes.

❌ Missing context
Check @page[Schedule]. Talk to @user[PM].
```

### Performance Considerations

- Mentions are resolved when content is processed
- Large numbers of mentions may slightly impact processing time
- Use mentions purposefully rather than excessively

## Troubleshooting

### Common Issues

**Mention Not Resolving:**

```markdown
# Check spelling and workspace access

❌ @page[Projct Plan] (typo)
✅ @page[Project Plan]

# Verify page exists and is accessible

❌ @page[Deleted Document]  
✅ @page[Current Document]
```

**Multiple Matches:**

```markdown
# Be more specific with titles

❌ @page[Report] (multiple "Report" pages)
✅ @page[Q4 Sales Report]
```

**Permission Issues:**

```markdown
# Ensure proper workspace access

❌ @database[Private Admin Data] (no access)
✅ @database[Team Shared Tasks]
```

### Fallback Behavior

When mentions can't be resolved:

- Original text displays as plain text
- No error messages or broken links
- Content remains readable and functional

## Integration Examples

### Project Updates

```markdown
## Weekly Update

**Progress:** @user[Development Team] completed features in @database[Sprint Backlog]

**Next Steps:**

- @user[QA Lead] will test new features
- Update documentation in @page[Feature Specifications]
- Review deployment plan with @user[DevOps Engineer]
```

### Meeting Notes

```markdown
# Team Standup - March 15

**Attendees:** @user[Sarah], @user[John], @user[Alice]

**Action Items:**

- @user[Sarah]: Update @page[Design System] with new components
- @user[John]: Resolve issues in @database[Bug Reports]
- @user[Alice]: Document API changes in @page[Developer Guide]
```

### Process Documentation

```markdown
## Onboarding Checklist

1. **Setup:** @user[HR Representative] provides workspace access
2. **Resources:** Review @page[Company Handbook] and @page[Team Guidelines]
3. **Tools:** Get added to @database[Project Assignments]
4. **Mentor:** Connect with @user[Team Lead] for guidance
```

## Related Documentation

- **[Rich Text Formatting](rich-text.md)** - Basic text styling
- **[Page Management](../page/index.md)** - Working with pages
- **[Database Operations](../database/index.md)** - Managing databases
- **[Workspace Discovery](../workspace/index.md)** - Finding content in your workspace
