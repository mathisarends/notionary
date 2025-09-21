# Colors & Highlights

Add visual emphasis to your content with colors and background highlights. Color formatting works across all text-based blocks and can be combined with other formatting options.

## Overview

Color formatting uses a simple syntax to apply text colors and background highlights. All colors follow Notion's standard color palette for consistency across your workspace.

## Basic Color Syntax

### Text Colors

Apply colors to text without changing the background:

```markdown
(red:urgent task)
(blue:information)
(green:completed)
```

### Background Highlights

Add colored backgrounds with contrasting text:

```markdown
(red_background:important warning)
(blue_background:key information)
(green_background:success message)
```

## Available Colors

### Standard Colors

All Notion colors are supported for both text and backgrounds:

**Text Colors:**

```markdown
(default:default text)
(gray:gray text)
(brown:brown text)
(orange:orange text)
(yellow:yellow text)
(green:green text)
(blue:blue text)
(purple:purple text)
(pink:pink text)
(red:red text)
```

**Background Colors:**

```markdown
(default_background:default highlight)
(gray_background:gray highlight)
(brown_background:brown highlight)
(orange_background:orange highlight)
(yellow_background:yellow highlight)
(green_background:green highlight)
(blue_background:blue highlight)
(purple_background:purple highlight)
(pink_background:pink highlight)
(red_background:red highlight)
```

## Combining with Other Formatting

### Colors with Rich Text

Combine colors with bold, italic, and other formatting:

```markdown
(red:**urgent deadline**)
(blue*background:\_important note*)
(green:~~completed~~ **done**)
```

### Colors with Links

Apply colors to linked content:

```markdown
(blue:[Documentation](https://docs.example.com))
(red_background:[**Critical Update**](https://alerts.company.com))
```

### Colors with Mentions

Highlight mentions with color formatting:

```markdown
(yellow_background:@user[Project Manager] needs to review this)
(red:Check with @user[Sarah] about @page[Budget Approval])
```

### Nested Color Formatting

Colors can contain complex nested formatting:

```markdown
(blue*background:**Project Update:** The \_new features* in @page[Release Notes] are `ready for testing`)
```

## Practical Examples

### Status Indicators

Use colors to show status and priority:

```markdown
## Task Status

- (green_background:✅ Completed) - Database migration
- (yellow_background:⏳ In Progress) - UI improvements
- (red_background:🔴 Blocked) - API integration
- (gray:📋 Not Started) - Documentation update
```

### Priority Levels

```markdown
**Project Priorities:**

1. (red:**HIGH**) - Security vulnerability fix
2. (orange:**MEDIUM**) - Performance optimization
3. (blue:**LOW**) - UI polish improvements
```

### Categorization

```markdown
## Meeting Types

- (purple_background:📋 Planning) - Strategy sessions
- (green_background:🔄 Standup) - Daily check-ins
- (blue_background:📊 Review) - Progress assessment
- (orange_background:🎯 Retrospective) - Team improvement
```

### Documentation Highlights

```markdown
(yellow_background:**Important:** Always backup data before running migrations)

(red_background:**Warning:** This action cannot be undone)

(green_background:**Success:** All tests are passing!)

(blue_background:**Info:** See the [API documentation](https://api.docs.com) for details)
```

## Best Practices

### Semantic Color Usage

Use colors consistently for meaning:

- **Red:** Warnings, errors, urgent items
- **Yellow:** Cautions, pending items, important notes
- **Green:** Success, completed items, positive status
- **Blue:** Information, neutral status, documentation
- **Purple:** Special categories, premium features
- **Gray:** Inactive, disabled, or archived items

### Accessibility Considerations

- Don't rely solely on color to convey information
- Use text indicators alongside color coding
- Maintain sufficient contrast for readability
- Be consistent with color meanings across your workspace

### Performance Tips

- Use color formatting purposefully, not excessively
- Combine with other formatting for better emphasis
- Keep color usage consistent throughout your content

## Troubleshooting

### Common Issues

**Invalid Color Names:**

```markdown
❌ (invalid_color:text)
✅ (red:text)
```

**Missing Colons:**

```markdown
❌ (red text)
✅ (red:text)
```

**Nested Parentheses:**

```markdown
❌ (red:(nested) text)
✅ (red:nested text)
```

## Related Features

- **[Rich Text Formatting](rich_text.md)** - Basic text styling
- **[Mentions](mentions.md)** - Reference users, pages, and databases
- **[Inline Equations](equations.md)** - Mathematical expressions
- **[Callouts](../callout.md)** - Block-level colored content
