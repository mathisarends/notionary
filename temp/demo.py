"""
demo_jarvis_clipboard_page.py
Creates a showcase page in Notion with the Builder API on 'Jarvis Clipboard'.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    print(f"🔎 Loading page by name: {PAGE_NAME!r}")
    page = await NotionPage.from_page_name(PAGE_NAME)

    # Optional: start clean for the demo (comment out if you just want to append)
    print("🧹 Clearing existing content …")
    await page.clear_page_content()

    print("🧱 Appending blocks via Builder API …")
    await page.append_markdown(
        lambda b: (
            b.h1("Jarvis Clipboard — Demo Page")
             .paragraph(
                 "This page demonstrates notionary’s MarkdownBuilder API: "
                 "structured blocks, media, diagrams, and nested content."
             )
             .callout("All reproducible from a single script. Perfect for demos & CI.", "🚀")
             .table_of_contents()
             .divider()

             # Column layout: main content + sidebar
             .columns(
                 # Main column (70%)
                 lambda col: (
                     col.h2("Getting Started")
                        .numbered_list(
                            [
                                "Load page: NotionPage.from_page_name(...)",
                                "Optionally clear existing content",
                                "Append blocks with the Builder API",
                            ]
                        )
                        .code(
                            'page = await NotionPage.from_page_name("Jarvis Clipboard")\n'
                            "await page.append_markdown(lambda b: b.h1('Title').paragraph('Text'))",
                            language="python",
                            caption="Minimal example: load page & append content",
                        )
                        .space()
                        .h2("Architecture Sketch (Mermaid)")
                        .mermaid(
                            """
                            flowchart LR
                                U[User] -->|prompts| A[LLM]
                                A --> B[Notionary MarkdownBuilder]
                                B --> C[Notion Blocks]
                                C --> N[Notion Page]
                                subgraph Media
                                  I[Image]:::m --> N
                                  V[Video]:::m --> N
                                  P[PDF]:::m --> N
                                end
                                classDef m stroke-dasharray:3 3;
                            """.strip(),
                            caption="High-level flow: Prompt → Builder → Notion",
                        )
                        .space()
                        # Use a plain toggle for the collapsible section (no table inside)
                        .toggle(
                            "Advanced Section",
                            lambda t: (
                                t.paragraph("Nested content within a collapsible section.")
                                 .bulleted_list(["Callouts", "Tables", "Todos"])
                                 .callout("Expand only if you care.", "💡")
                                 .todo_list(
                                     ["Link the README", "Record screencast", "Post tweet"],
                                     completed=[True, False, False],
                                 )
                            ),
                        )
                        # Put the table as a sibling block (outside the toggle)
                        .h3("Feature Matrix")
                        .table(
                            headers=["Feature", "Status"],
                            rows=[
                                ["Columns", "✅"],
                                ["Mermaid", "✅"],
                                ["PDF/Bookmark/Image", "✅"],
                            ],
                        )
                 ),
                 # Sidebar (30%)
                 lambda col: (
                     col.h3("Quick Links")
                        .bookmark("https://github.com/yourname/notionary", title="Repository")
                        .bookmark("https://www.notion.so/", title="Notion")
                        .space()
                        .h3("Media")
                        .image(
                            "https://images.unsplash.com/photo-1518779578993-ec3579fee39f",
                            caption="Demo Image — Unsplash",
                        )
                        .pdf(
                            "https://arxiv.org/pdf/2106.01345.pdf",
                            caption="Sample PDF (external)",
                        )
                        .embed(
                            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            caption="YouTube embed (example)",
                        )
                 ),
                 width_ratios=[0.7, 0.3],
             )
             .divider()
             .h2("Next Steps")
             .paragraph(
                 "• Re-deploy via script in a reproducible way\n"
                 "• Integrate into CI (e.g., auto-publish release notes to Notion)\n"
                 "• Record a short screencast (OBS/Screen Studio)"
             )
        )
    )

    print("✅ Blocks appended successfully!")
    preview = await page.get_text_content()
    print("📄 Preview (first 400 chars):")
    print(preview[:400] + ("…" if len(preview) > 400 else ""))


if __name__ == "__main__":
    asyncio.run(main())
