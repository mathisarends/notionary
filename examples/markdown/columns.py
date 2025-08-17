import asyncio
from notionary import NotionPage
from notionary.markdown.markdown_builder import MarkdownBuilder


async def main():
    """Minimal column test to isolate parsing issues."""

    try:
        page = await NotionPage.from_page_name("Jarvis Clipboard")
        builder = MarkdownBuilder()

        builder.h1("Complex Page Layout Test")

        # Complex 3-column layout with all elements
        builder.columns(
            # Left Column - Navigation & Info
            lambda col: (
                col.h2("Navigation")
                .bulleted_list(["Home", "About", "Services", "Contact"])
                .divider()
                .callout("Welcome to our site!", "👋")
                .todo("Setup navigation", True)
                .todo("Add footer", False)
                .space()
                .quote("Great design is invisible")
            ),
            # Middle Column - Main Content
            lambda col: (
                col.h1("Main Content")
                .paragraph("This is the main content area with rich elements.")
                .toggle("Code Examples", lambda t: (
                    t.h3("Python Code")
                    .code("def hello():\n    print('Hello World!')", "python", "Simple function")
                    .paragraph("This toggle contains code examples.")
                ))
                .toggleable_heading("Advanced Section", 2, lambda t: (
                    t.numbered_list(["First step", "Second step", "Third step"])
                    .table(["Feature", "Status", "Priority"], [
                        ["Authentication", "Done", "High"],
                        ["API", "In Progress", "Medium"],
                        ["UI", "Planned", "Low"]
                    ])
                    .equation("E = mc^2")
                ))
                .breadcrumb()
                .table_of_contents("blue")
            ),
            # Right Column - Media & Utils
            lambda col: (
                col.h2("Media & Tools")
                .paragraph("Simple text content without external URLs")
                .callout("Note: External media removed", "⚠️")
                .equation("f(x) = x^2 + 2x + 1")
                .code("SELECT * FROM users WHERE active = true;", "sql", "Database query")
                .mermaid("""graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]""", "Simple flowchart")
            ),
                    width_ratios=[0.25, 0.5, 0.25],
                    )

        markdown_content = builder.build()

        print("markdown_content", markdown_content)

        print("Generated markdown:")
        print(markdown_content)
        print("=" * 50)

        await page.append_markdown(markdown_content)
        print("✅ Success!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
