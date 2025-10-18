Checkbox tasks for tracking completion. Supports nesting, child blocks, and rich text.

## Syntax

Unchecked:
```markdown
- [ ] Buy groceries
- [ ] Finish homework
```

Checked:
```markdown
- [x] Completed task
```

You can nest child blocks (paragraphs, todos, lists) by indenting them with four spaces:

```markdown
- [ ] Main task
	Additional notes
	- [ ] Sub-task
	- [x] Done sub-task
```

## Examples

Simple list:
```markdown
- [ ] Write docs
- [x] Review PRs
- [ ] Plan release
```

With nested children:
```markdown
- [ ] Prepare meeting
	Agenda:
	- [ ] Slides
	- [ ] Demo
	- [x] Confirm room
	Notes for team
```

Mixed with paragraphs and lists:
```markdown
- [ ] Research topic
	- Key points
		1. Read papers
		2. Summarize findings
	Next steps
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (
	MarkdownBuilder()
	  .todo("Write docs")
	  .checked_todo("Review PRs")
	  .todo("Prepare meeting", builder_func=lambda b: (
		  b.paragraph("Agenda:")
		   .todo("Slides")
		   .todo("Demo")
		   .checked_todo("Confirm room")
		   .paragraph("Notes for team")
	  ))
	  .build()
)
```


## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on todo blocks, see <a href="https://developers.notion.com/reference/block#to-do" target="_blank">https://developers.notion.com/reference/block#to-do</a>
