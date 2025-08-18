# Code Blocks

Code blocks display syntax-highlighted code with support for 70+ programming languages.

## Basic Syntax

````markdown
```language
code content here
```
````

## Quick Examples

````markdown
```python
def hello():
    return "Hello, Notionary!"
```

```javascript
const greet = (name) => `Hello, ${name}!`;
```

```bash
pip install notionary
```

```json
{ "name": "notionary", "version": "1.0.0" }
```
````

## With Captions

````markdown
```python "Authentication example"
import os
from notionary import NotionClient

client = NotionClient(token=os.getenv("NOTION_TOKEN"))
```
````

## Programmatic Usage

### Using MarkdownBuilder

```python
from notionary.markdown.markdown_builder import MarkdownBuilder

builder = (MarkdownBuilder()
    .h2("API Examples")
    .code("pip install notionary", "bash")
    .code('print("Hello, world!")', "python", "Basic example")
    .mermaid("graph TD; A-->B; B-->C;", "Flow diagram")
)

print(builder.build())
```

## Supported Languages

Notionary supports 70+ programming languages including:

**Popular Languages:** `python`, `javascript`, `typescript`, `java`, `c++`, `c#`, `go`, `rust`, `swift`, `kotlin`

**Web Technologies:** `html`, `css`, `scss`, `sass`, `less`

**Functional:** `haskell`, `erlang`, `elixir`, `f#`, `clojure`, `scheme`, `lisp`

**Data Formats:** `json`, `yaml`, `xml`, `sql`, `csv`

**Scripting:** `bash`, `shell`, `powershell`, `perl`, `ruby`

**Scientific:** `r`, `matlab`, `julia`

**Markup:** `markdown`, `latex`

**Other:** `docker`, `nginx`, `protobuf`, `graphql`, `mermaid`

### Complete Language List

```python
from notionary.blocks.code import CodeLanguage

# All supported languages
print(list(CodeLanguage))
# ['abap', 'arduino', 'bash', 'basic', 'c', 'clojure', ...]
```

## Reference

For detailed language support and formatting options, see the [Notion API Code Block Reference](https://developers.notion.com/reference/block#code).

```

```
