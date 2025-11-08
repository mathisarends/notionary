# Synced Block

Represents a Notion Synced Block. Content can be nested using indentation (4 spaces per level), similar to the Toggle block.

> Limitation: Creating a brand‑new (original) Synced Block via markdown is **not** supported. Only referencing an existing synced block with `Synced from: <block-id>` is processed.

## Syntax

Original (render-only marker – cannot create a new original block):

```markdown
>>> Synced Block
	Child content inside the original synced block context.
```

Duplicate reference (supported):

```markdown
>>> Synced from: 12345678-90ab-cdef-1234-567890abcdef
	Optional nested content shown under the referenced synced block.
```

Rules:
- Use exactly three `>` characters followed by a space.
- `Synced from:` must be followed by a valid block UUID (with dashes) to be recognized.
- Nested lines are indented with 4 spaces per level.
- If no child content is provided, only the reference line is rendered.

## Examples

Duplicate with nested list:

```markdown
>>> Synced from: e3a1a4b2-8f8b-4a13-9a90-0c1f7c2a9f11
	- This checklist appears under the synced reference
	- You can mix in other block syntaxes
```

Original marker placeholder (no creation):

```markdown
>>> Synced Block
	No content available
```

Multiple references:

```markdown
>>> Synced from: 11111111-2222-3333-4444-555555555555
	Some contextual note.

>>> Synced from: 66666666-7777-8888-9999-aaaaaaaaaaaa
	- Task A
	- Task B
```

## Reference

!!! info "Notion API Reference"
	Official Notion API docs for synced blocks: <a href="https://developers.notion.com/reference/block#synced-blocks" target="_blank">https://developers.notion.com/reference/block#synced-blocks</a>
