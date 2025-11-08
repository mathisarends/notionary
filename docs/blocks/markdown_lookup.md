## Markdown syntax prompts for agents

Get AI‑ready, structured descriptions of Notionary’s markdown syntax from a single, high‑level API: `SyntaxPromptRegistry`.

This registry exposes human‑readable prompt data for every supported block type, including few‑shot examples you can feed directly in LLM prompts. It gives agents precise context for valid Notionary markdown, acts as the single source of truth for supported elements, and can export everything as JSON for tooling or automated docs.

### What you get per element

Each entry is a `SyntaxPromptData` with the fields:

- `element`: Display name, e.g. "Image", "Quote"
- `description`: Short guidance for when/how to use
- `is_multi_line`: Whether the element spans multiple lines
- `few_shot_examples`: Valid examples you can copy into your prompts
- `usage_notes`: Additional constraints or tips (e.g., URL vs local path rules)
- `supports_inline_rich_text`: Whether inline rich text is allowed inside

### Quick start

```python
from notionary import SyntaxPromptRegistry

registry = SyntaxPromptRegistry()

# Get a single element’s prompt data (e.g., Image)
image_prompt = registry.get_image_prompt()
print(image_prompt.element)           # "Image"
print(image_prompt.description)       # human-readable usage guidance
print(image_prompt.few_shot_examples) # ready-to-use examples

# Get everything as JSON (keys mapped to data)
all_prompts_json = registry.get_all_prompt_data_as_json_string(indent=2)
print(all_prompts_json)
```

### Example: use few‑shots in an LLM system prompt

```python
from notionary import SyntaxPromptRegistry

registry = SyntaxPromptRegistry()

audio = registry.get_audio_prompt()
image = registry.get_image_prompt()
quote = registry.get_quote_prompt()

system_context = f"""
You produce Notionary markdown. Follow these element rules.

{audio.element}: {audio.description}
Examples:\n- " + "\n- ".join(audio.few_shot_examples) + "\n\n"

{image.element}: {image.description}
Examples:\n- " + "\n- ".join(image.few_shot_examples) + "\n\n"

{quote.element}: {quote.description}
Examples:\n- " + "\n- ".join(quote.few_shot_examples) + "\n\n"
"""
```

### Export everything for tools

If you want to surface available elements dynamically, use the JSON export and feed it into your tool’s help UI or docs generator:

```python
from notionary import SyntaxPromptRegistry

prompts = SyntaxPromptRegistry().get_all_prompt_data_as_json(indent=2)
# Write to a file, index it for search, etc.
```
