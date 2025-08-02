from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")
    print(f"Page found: {page.title}")

    # Test markdown with advanced capability-based features
    test_markdown = """## 🚀 Capability-based Parser Test

This markdown tests the new **priority-based** and **context-aware** parsing system.

### 📋 Basic Elements Test

Here's a simple paragraph with **bold** and *italic* formatting.

- [ ] Todo item one  
- [x] Completed todo item
- [ ] Another todo item

- Regular bullet point
- Another bullet point with `inline code`

1. Numbered list item
2. Second numbered item
3. Third item with [link](https://example.com)

### 🔄 Toggle Elements Test (Priority: 10)

        | Header 1 | Header 2 | Header 3 |
        | -------- | -------- | -------- |
        | Cell 1   | Cell 2   | Cell 3   |
        | Cell 4   | Cell 5   | Cell 6   |
### 🎯 Complex Nesting Test



### 📝 Mixed Content Test

[callout](🚨 Important: This tests priority-based parsing "🔥")

Here's a paragraph between callout and divider.

---

### 🔍 Edge Cases Test

This paragraph should be parsed AFTER headings (priority 8) but BEFORE other content.

## This heading should be parsed with priority 8

+++ This toggle should be parsed with priority 10

### 📋 Context-Aware Testing

These pipes should NOT be parsed as toggle content because they're not in toggle context:
| This should be a normal paragraph
| This should also be a normal paragraph

But inside a toggle:
+++ Context Test
| These pipes SHOULD be parsed as toggle content
| Because we're inside a toggle context
| The parser should be context-aware!

### 🏁 Final Validation

- [ ] Parser handles priorities correctly
- [ ] Context-aware parsing works  
- [ ] Nested structures render properly
- [ ] Tables work in all contexts
- [ ] No hardcoded special cases needed

[quote](The new architecture eliminates hardcoded logic and makes the parser truly extensible! 🎉)"""

    # Test the new capability-based parser
    print("\n🚀 Testing new capability-based parser...")
    appended_content = await page.append_markdown(test_markdown, append_divider=False)

    if appended_content:
        print(f"✅ Successfully appended {len(appended_content)} characters")

        # Show some stats about what was parsed
        lines = test_markdown.split("\n")
        toggle_lines = [line for line in lines if line.startswith("+++")]
        pipe_lines = [line for line in lines if line.startswith("|")]
        table_lines = [
            line for line in lines if "|" in line and not line.startswith("|")
        ]

        print("\n📊 Parsing Statistics:")
        print(f"   Toggle headers: {len(toggle_lines)}")
        print(f"   Pipe content lines: {len(pipe_lines)}")
        print(f"   Table-like lines: {len(table_lines)}")
        print(f"   Total lines processed: {len(lines)}")

        print(f"\n🔗 View result: {page.url}")

    else:
        print("❌ Failed to append content")

    # Test edge cases specifically
    print("\n🧪 Testing edge cases...")

    edge_case_markdown = """
### Edge Case: Mixed Pipe Lines

These should be paragraphs (no toggle context):
| Not toggle content
| Also not toggle content

+++ But This Is A Toggle
| This IS toggle content
| So is this line
| And this one too

Back to normal paragraphs:
| This should be a paragraph again
| Because we're out of toggle context
"""

    edge_result = await page.append_markdown(edge_case_markdown, append_divider=True)
    if edge_result:
        print("✅ Edge case test completed successfully")
    else:
        print("❌ Edge case test failed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
