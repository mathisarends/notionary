"""
# Notionary: Page Lookup Example
===============================

This example demonstrates how to locate an existing Notion page
using the NotionPageFactory.

It showcases the easiest way to access a page by its name,
but also mentions alternatives like lookup by ID or URL.

IMPORTANT: Replace "Jarvis fitboard" with the actual name of your page.
The factory uses fuzzy matching to find the closest match.
"""

import asyncio
import traceback
from notionary import NotionPageFactory

YOUR_PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demonstrates various ways to find a Notion page."""

    try:
        print("Searching for page by name...")
        page = await NotionPageFactory.from_page_name(YOUR_PAGE_NAME)

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )

        print(f'✅ Found: "{title}" {icon} → {url}')

        python_documentation = """## Comprehensive Python Project Documentation

### Project Overview
This is a **comprehensive** project that explores *advanced* Python `data science` and machine learning techniques.

<!-- spacer -->

!> [🧠] Project Intelligence Framework
| Our mission is to create **cutting-edge** computational tools
| that solve complex real-world problems.

### Key Project Components

1. Data Processing Utilities
2. Machine Learning Modules
3. Visualization Techniques

<!-- spacer -->

### Code Demonstration
```python
class DataProcessor:
    def __init__(self, data_source):
        self.data = data_source
    
    def transform(self, method='standard'):
        if method == 'standard':
            return self._standard_transform()
        elif method == 'advanced':
            return self._advanced_transform()
```

### Interactive Todo List
- [ ] Implement core data processing algorithm
- [ ] Write comprehensive unit tests
- [x] Create project documentation
- [ ] Optimize performance metrics

### External Resources
[bookmark](https://docs.python.org "Python Official Documentation")
[bookmark](https://scikit-learn.org "Machine Learning Library")

<!-- spacer -->

### Embedded Content
<embed:Project Resources>(https://drive.google.com/drive/folders/project_resources)

### Quotes and Insights
> "Innovation distinguishes between a leader and a follower." - Steve Jobs

<!-- spacer -->

### Toggleable Technical Details
+++ Advanced Implementation Notes
| **Key Considerations:**
| - *Performance optimization*
| - `Scalable architecture`
| - __Error handling strategies__

### Sample Table of Metrics
| Metric | Value | Status |
| ------ | ----- | ------ |
| Accuracy | 92.5% | ✅ |
| Processing Speed | 0.03s | ✅ |
| Memory Usage | 128MB | ⚠️ |

### Final Thoughts
Some **critical** points to remember:
- *Readability* is paramount
- `Clean code` speaks volumes
- __Continuous learning__ drives innovation

### Mentions and Collaborators
Check detailed notes at @[project-main-doc]

### Image Visualization
![Data Flow Diagram](https://example.com/data-flow.png)
        """

        """ result = await page.append_markdown(python_documentation)
        print(f"✅ Markdown appended: {result}") """

        prompt = page.block_registry.generate_llm_prompt()
        print(f"Prompt: {prompt}")

    except Exception as e:
        print(f"❌ Error while loading page from URL: {traceback.format_exc(e)}")


if __name__ == "__main__":
    print("🚀 Starting Notionary URL Lookup Example...")
    found_page = asyncio.run(main())
