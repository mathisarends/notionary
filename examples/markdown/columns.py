import asyncio

from notionary import MarkdownBuilder, NotionPage


async def main():
    """Minimal column test to isolate parsing issues."""

    try:
        page = await NotionPage.from_title("Jarvis Clipboard")
        builder = MarkdownBuilder()

        builder.h1("Minimal Columns + Toggle Test")

        builder.columns(
            lambda col: (
                col.paragraph("Left column start").toggleable_heading(
                    "Left toggle", 2, lambda t: t.paragraph("inside left toggle")
                )
            ),
            lambda col: (
                col.paragraph("Right column start").toggle("Right toggle", lambda t: t.paragraph("inside right toggle"))
            ),
            width_ratios=[0.5, 0.5],
        )

        markdown_content = builder.build()
        print("Generated markdown:")
        print(markdown_content)

        await page.append_markdown(markdown_content)
        print("✅ Appended minimal columns example")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
