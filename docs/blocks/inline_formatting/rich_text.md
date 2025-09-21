# Rich Text Formatting

Rich text formatting adds visual emphasis and structure to your content. All formatting works across paragraphs, headings, callouts, lists, and other text-based blocks.

## Basic Formatting

### Bold Text

Use double asterisks for **strong emphasis**.

```markdown
**This text is bold**
This is **partially bold** text
```

**Result:** **This text is bold**

### Italic Text

Use single asterisks or underscores for _emphasis_.

```markdown
_This text is italic_
_This text is also italic_
Mixed with **bold and _italic_**
```

**Result:** _This text is italic_

### Underline

Use double underscores for **underlined text**.

```markdown
**This text is underlined**
**Important:** regular text follows
```

**Result:** <u>This text is underlined</u>

### Strikethrough

Use double tildes for ~~deleted or crossed-out~~ content.

```markdown
~~This text is crossed out~~
Original price: ~~$99~~ Now: **$49**
```

**Result:** ~~This text is crossed out~~

### Inline Code

Use backticks for `code snippets` and technical terms.

```markdown
Use the `install` command to set up the package
The variable `user_name` stores the login information
```

**Result:** Use the `install` command to set up the package

## Combining Formats

### Multiple Formats

Combine different formatting types for complex styling:

```markdown
**Bold _and italic_** text
**Underlined and **bold**** content
~~Struck through with _italic_~~ text
```

### Nested Formatting

Layer formatting for sophisticated emphasis:

```markdown
_This is italic with **bold inside** and continues_
**Bold text with `code snippet` embedded**
**Underlined with **bold** and _italic_ sections**
```

## Links

### Basic Links

Create clickable links with bracket notation:

```markdown
[Notion Homepage](https://notion.so)
Check out the [documentation](https://developers.notion.com) for details
```

### Links with Formatting

Apply formatting to link text:

```markdown
[**Important Link**](https://example.com)
[_Documentation_](https://docs.example.com)
Visit our [~~old~~ **new**](https://new.example.com) website
```

### Links in Context

Integrate links naturally within formatted text:

```markdown
**Important:** Please review the [quarterly report](https://reports.company.com) before the meeting
```

## Practical Examples

### Documentation

```markdown
**Getting Started:** Install the package using `npm install notionary` and follow the [setup guide](https://docs.notionary.com/setup).
```

### Task Lists

```markdown
- **High Priority:** Complete the ~~draft~~ _final_ version by **Friday**
- Review the `config.json` file and update [deployment settings](https://deploy.company.com)
```

### Callouts with Rich Text

```markdown
[callout](**Warning:** The `production` environment requires **careful testing** before deployment)
```

### Table Content

```markdown
| Task                | Status        | Notes                                     |
| ------------------- | ------------- | ----------------------------------------- |
| **API Integration** | _In Progress_ | See [documentation](https://api.docs.com) |
| ~~Legacy Support~~  | **Complete**  | `deprecated` functions removed            |
```

## Best Practices

### Semantic Formatting

- **Bold** for important concepts and strong emphasis
- _Italic_ for subtle emphasis and introduction of terms
- `Code` for technical terms, commands, and file names
- ~~Strikethrough~~ for outdated or deleted content

### Readability Guidelines

```markdown
✅ Good - Clear and purposeful
**Project Status:** The _initial phase_ is complete. Next: update `config.yaml` and deploy.

❌ Avoid - Over-formatted and hard to read
**_~~Important~~_** **_update_**: **check** the `file` **now**
```

### Consistency Tips

- Use the same formatting pattern throughout your workspace
- **Bold** for section headers in lists and callouts
- _Italic_ for introducing new concepts or terms
- `Code formatting` consistently for all technical references

## Troubleshooting

### Common Issues

**Missing Spaces:** Ensure spaces around formatting markers

```markdown
❌ word**bold**word
✅ word **bold** word
```

**Nested Quotes:** Use different quote types to avoid conflicts

```markdown
❌ "The command is "install package" to begin"
✅ "The command is `install package` to begin"
```

**Special Characters:** Use backslashes to escape formatting characters

```markdown
❌ The price is $**50**
✅ The price is \$**50**
```

## Related Features

- **[Mentions](mentions.md)** - Reference users, pages, and databases
- **[Colors & Highlights](colors_and_highlights.md)** - Add visual emphasis with color
- **[Inline Equations](equations.md)** - Mathematical expressions
- **[Block Formatting](../index.md)** - Structure content with specialized blocks
