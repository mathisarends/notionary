# Rich Text

Rich text is the inline format used everywhere: page titles, paragraphs, list items, callouts, table cells, captions. Notionary lets you author it in `readable Markdown` (plus a few tiny extensions) and converts it reliably to / from Notion’s JSON objects.

**Why it matters**

- One way to write formatting, mentions, colors, equations
- Human friendly authoring; API objects handled for you
- Safe round‑trip (what you don’t know, you don’t need to learn)

### Mentions

You can reference pages, databases, users and dates/ranges via so called `mentions`:

- `@page[Roadmap]`
- `@database[Features]`
- `@user[Alice Smith]`
- `@date[2025-10-01]` or `@date[2025-10-01–2025-10-07]`

You may also put the raw UUID (page / database / user id) inside the brackets, but using names is easier to read and maintain.

> Notionary always returns the matched entity NAME (never the id) when you read rich text back. If something cannot be resolved it is left exactly as you authored it (no hidden failures).

---

## Quick Formatting Reference

| Purpose          | Markdown You Write                                   | Example                        |
| ---------------- | ---------------------------------------------------- | ------------------------------ |
| Bold             | `**text**`                                           | `**Bold**`                     |
| Italic           | `_text_` or `*text*`                                 | `_Italic_`                     |
| Underline        | `__text__`                                           | `__Underline__`                |
| Strikethrough    | `~~text~~`                                           | `~~Old~~`                      |
| Inline code      | `` `code` ``                                         | `` `print()` ``                |
| Link             | `[label](https://…)`                                 | `[Site](https://example.com)`  |
| Color            | `(red:important!)`                                   | `(orange:Heads up)`            |
| Inline equation  | `$E = mc^2$`                                         | `$a^2 + b^2 = c^2$`            |
| Page mention     | `@page[Title]`                                       | `@page[Architecture Overview]` |
| Database mention | `@database[Name]`                                    | `@database[Sales Pipeline]`    |
| User mention     | `@user[Full Name]`                                   | `@user[Jane Doe]`              |
| Date / range     | `@date[2025-10-01]` / `@date[2025-10-01–2025-10-07]` | `@date[2025-12-01–2025-12-15]` |

### Behavior Notes (Kept Short)

- Unknown colors: left exactly as written `(weirdColor:Text)`
- Unresolved mentions: left as `@page[Whatever]` (so you notice & can fix)
- Inline code blocks stop further formatting inside backticks
- No auto‑healing of half‑written markers (you keep control)

---

## More Examples

Simple release note:

```markdown
Release **v1.4** adds (green:performance gains) and fixes ~~deprecated~~ APIs.
See @page[Architecture Overview] and talk to @user[Lisa Müller].
Deployment window: @date[2025-10-02–2025-10-03].
Reference: [Design Doc](https://internal/wiki/spec)
```

Colors + nesting:

```markdown
This is (orange:very **important** information) you should read.
```

Equations & links together:

```markdown
Energy formula: `$E = mc^2$` explained in [Docs](https://physics.example).
```

Fallback illustration (unknown color + unresolved mention):

```markdown
(ultraviolet:Edge) assigned to @user[Ghost Person]
```

Result: color token + mention remain unchanged so you can correct them later.

Page vs id (both valid):

```markdown
@page[Roadmap] == @page[3d2f1c1a-4b55-4a20-9c6a-7fa9f5c5d111]
```

When read back both display using the page title if resolvable.

## Reference

!!! info "Notion API Reference"
For the official Notion API reference on blocks, see [https://developers.notion.com/reference/rich-text](https://developers.notion.com/reference/rich-text)
