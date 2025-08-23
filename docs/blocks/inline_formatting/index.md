# Inline Formatting

Notionary supports comprehensive inline formatting that works across all text-based blocks including paragraphs, headings, callouts, lists, and more.

## Overview

Inline formatting allows you to add emphasis, structure, and interactivity to your text content without creating separate blocks. All formatting can be combined and nested for complex styling.

## Formatting Categories

### **[Rich Text Formatting](rich_text.md)**

Basic text styling including bold, italic, underline, strikethrough, and inline code.

```markdown
**Bold text**, _italic text_, **underlined text**, ~~strikethrough~~, `inline code`
```

### **[Mentions](mentions.md)**

Reference pages, databases, and users in your workspace with auto-linking.

```markdown
Check out @page[Project Overview] and ask @user[Sarah] about @database[Tasks]
```

### **[Colors & Highlights](colors_and_highlights.md)**

Add color and background highlights to emphasize important content.

```markdown
(red:urgent task) and (blue_background:important note)
```

### **[Inline Equations](equations.md)**

Mathematical expressions using LaTeX syntax.

```markdown
The formula is $E = mc^2$ for energy calculation.
```

## Combining Formatting

All inline formatting can be combined and nested:

```markdown
(red*background:**@user[Sarah]** needs to review the \_important* changes in @page[Q4 Planning])
```

This creates: red background text with bold user mention, italic emphasis, and page link.

## Supported Blocks

Inline formatting works in all text-containing blocks:

- **[Paragraphs](../paragraph.md)** - Full formatting support
- **[Headings](../heading.md)** - All formatting types
- **[Callouts](../callout.md)** - Rich text with colors
- **[Lists](../bulleted_list.md)** - Formatted list items
- **[Quotes](../quote.md)** - Styled quotations
- **[Tables](../table.md)** - Formatted cell content
- **[Toggles](../toggle.md)** - Rich toggle titles and content

## Best Practices

### Readability First

- Use formatting to enhance meaning, not just decoration
- Avoid over-formatting that makes text hard to scan
- Be consistent with color usage across your workspace

### Performance Considerations

- Mentions are resolved automatically but require workspace access
- Complex nested formatting may take slightly longer to process
- Use formatting purposefully rather than excessively

### Accessibility

- Color coding should supplement, not replace, other indicators
- Use semantic formatting (bold for importance, italic for emphasis)
- Provide context for mentions when sharing outside your workspace

## Related Documentation

- **[Block Types](../index.md)** - All supported content blocks
- **[Page Management](../../page/index.md)** - Working with page content

---

Ready to get started? Begin with **[Rich Text Formatting](rich_text.md)** for the basics.
