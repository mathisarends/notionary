"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio

from notionary import NotionPage
from notionary.blocks.markdown.markdown_document_model import MarkdownDocumentModel
from notionary.blocks import ColumnMarkdownNode, ColumnListMarkdownNode, ParagraphMarkdownNode

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        # Create a MarkdownDocumentModel instead of raw markdown string
        document_model = MarkdownDocumentModel(
            blocks=[
                ColumnListMarkdownNode(
                    columns=[
                        ColumnMarkdownNode(
                            children=[
                                ParagraphMarkdownNode(text="test")
                            ]
                        ),
                        ColumnMarkdownNode(
                            children=[
                                ParagraphMarkdownNode(text="fest")
                            ]
                        )
                    ]
                )
            ]
        )

        # Pass the MarkdownDocumentModel directly
        await page.append_markdown(document_model)

        print("✅ Successfully added all caption syntax examples!")

        content = await page.get_text_content()
        print(f"📄 Page content preview:\n{content[:500]}...")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
