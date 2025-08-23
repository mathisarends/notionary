"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified (caption:...) behavior we just implemented!
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        markdown = """
# 🎯 Caption Syntax Test - All Media Elements

## 🎵 Audio Elements with Captions

Basic audio with caption:
[audio](https://www.soundjay.com/misc/sounds/bell-ringing-05.wav)(caption:Bell sound effect)

Audio with emoji caption:
[audio](https://www.soundjay.com/misc/sounds/bell-ringing-05.wav)(caption:🔔 Ring ring!)

Audio with nested parentheses:
[audio](https://www.soundjay.com/misc/sounds/bell-ringing-05.wav)(caption:Audio file (with nested) content)

## 📄 File Elements with Captions

PDF with German caption:
[file](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf)(caption:Wichtiges Dokument für das Projekt)

Excel file with technical caption:
[file](https://file-examples.com/storage/fe68c8d85d4341c8dc7ad52/2017/10/file_example_XLS_10.xls)(caption:Finanzdaten Q4 (2024))

PowerPoint with special formatting:
[file](https://file-examples.com/storage/fe68c8d85d4341c8dc7ad52/2017/08/file_example_PPT_500kB.ppt)(caption:**Präsentation** - Neues Marketing-Konzept)

## 🔗 Bookmark Elements with Captions

GitHub repository:
[bookmark](https://github.com/mathisarends/notionary)(caption:Notionary - Python Notion API)

Website with description:
[bookmark](https://www.notion.so)(caption:Notion - The all-in-one workspace)

Bookmark with separator:
[bookmark](https://python.org)(caption:Python.org - Official Python Website)

## ⚡ Edge Cases and Complex Scenarios

Multiple media elements in sequence:
[audio](https://www.soundjay.com/misc/sounds/bell-ringing-05.wav)(caption:Audio between images)

Empty captions (should work):
[file](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf)(caption:)

Caption with line breaks and formatting:
[bookmark](https://docs.python.org)(caption:Python Documentation - **Complete** reference for Python programming)

## 🧪 Mathematical Content

Equation blocks (different syntax):
$$E = mc^2$$

$$\\frac{a}{b} = \\frac{c}{d}$$

$$\\sum_{i=1}^n i = \\frac{n(n+1)}{2}$$

## 📝 Text Formatting Tests

Inline formatting with colors:
This is **bold** text with {blue:blue color} and {red:red color}.

Text with mentions and equations:
Check out this formula $x^2 + y^2 = z^2$ for the Pythagorean theorem.

---

## ✅ Test Summary

This document tests:
- ✅ Basic caption syntax: `(caption:text)`
- ✅ Special characters in captions: `!?&/()`
- ✅ Unicode support: `🌟 中文 äöüß`
- ✅ Whitespace preservation
- ✅ Nested parentheses in captions
- ✅ Rich text formatting in captions
- ✅ Caption position flexibility
- ✅ All media element types
- ✅ Edge cases and empty captions

If you can see all the media elements above with their proper captions, 
then our caption syntax implementation is working perfectly! 🎉
"""

        print("📝 Adding comprehensive caption syntax test content...")
        await page.append_markdown(markdown)

        print("✅ Successfully added all caption syntax examples!")
        print("\n🔍 Testing individual elements...")

        # Test individual conversions to verify they work
        from notionary.blocks.image_block.image_element import ImageElement
        from notionary.blocks.audio.audio_element import AudioElement
        from notionary.blocks.file.file_element import FileElement
        from notionary.blocks.bookmark.bookmark_element import BookmarkElement

        test_cases = [
            ("[image](https://example.com/test.jpg)(caption:Test Image)", ImageElement),
            ("[audio](https://example.com/test.mp3)(caption:Test Audio 🎵)", AudioElement),
            ("[file](https://example.com/test.pdf)(caption:Important Document)", FileElement),
            ("[bookmark](https://example.com)(caption:Example Website)", BookmarkElement),
            ("[image](https://example.com/special.png)(caption:Special chars !?&/())", ImageElement),
            ("[audio](https://example.com/song.wav)(caption:  Whitespace test  )", AudioElement),
        ]

        print("\n🧪 Individual element conversion tests:")
        for markdown_text, element_class in test_cases:
            result = element_class.markdown_to_notion(markdown_text)
            if result:
                print(f"✅ {element_class.__name__}: {markdown_text[:50]}...")
            else:
                print(f"❌ {element_class.__name__}: FAILED - {markdown_text[:50]}...")

        content = await page.get_text_content()
        print(f"\n📄 Page created successfully! Content length: {len(content)} characters")
        print(f"🌐 Check your Notion page '{PAGE_NAME}' to see all the caption examples!")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")
        print("💡 Or create a new page with that name in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
