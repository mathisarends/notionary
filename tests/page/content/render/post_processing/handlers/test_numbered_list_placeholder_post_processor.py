import pytest

from notionary.page.content.renderer.post_processing.handlers import NumberedListPlaceholderReplaceerPostProcessor


@pytest.fixture
def processor() -> NumberedListPlaceholderReplaceerPostProcessor:
    return NumberedListPlaceholderReplaceerPostProcessor()


def test_empty_string_should_pass(processor: NumberedListPlaceholderReplaceerPostProcessor) -> None:
    result = processor.process("")
    assert result == ""


def test_only_whitespace_should_pass(processor: NumberedListPlaceholderReplaceerPostProcessor) -> None:
    markdown = "   \n\n  \t"
    result = processor.process(markdown)
    assert result == markdown


def test_text_without_placeholders_should_pass_unchanged(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "# Normal heading\n\nNormal text without lists.\n\n## Another heading\n\n- List\n- Items"
    result = processor.process(markdown)
    assert result == markdown


def test_placeholder_should_be_replaced_with_sequential_numbers(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "__NUM__. First item\n__NUM__. Second item\n__NUM__. Third item"
    expected = "1. First item\n2. Second item\n3. Third item"

    result = processor.process(markdown)
    assert result == expected


def test_single_placeholder_item_should_become_number_one(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "__NUM__. Single item"
    expected = "1. Single item"

    result = processor.process(markdown)
    assert result == expected


def test_multiple_separate_lists_should_reset_counter(processor: NumberedListPlaceholderReplaceerPostProcessor) -> None:
    markdown = (
        "__NUM__. First item\n"
        "__NUM__. Second item\n"
        "\n"
        "Some paragraph text\n"
        "\n"
        "__NUM__. First item again\n"
        "__NUM__. Second item again"
    )
    expected = "1. First item\n2. Second item\n\nSome paragraph text\n\n1. First item again\n2. Second item again"

    result = processor.process(markdown)
    assert result == expected


def test_blank_lines_between_list_items_should_be_removed(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "__NUM__. First item\n\n__NUM__. Second item\n\n__NUM__. Third item"
    expected = "1. First item\n2. Second item\n3. Third item"

    result = processor.process(markdown)
    assert result == expected


def test_blank_lines_after_list_should_be_preserved(processor: NumberedListPlaceholderReplaceerPostProcessor) -> None:
    markdown = "__NUM__. First item\n__NUM__. Second item\n\nSome text here"
    expected = "1. First item\n2. Second item\n\nSome text here"

    result = processor.process(markdown)
    assert result == expected


def test_list_items_with_markdown_formatting_should_preserve_content(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "__NUM__. Item with **bold** and _italic_\n__NUM__. Item with [link](url)\n__NUM__. Item with `code`"
    expected = "1. Item with **bold** and _italic_\n2. Item with [link](url)\n3. Item with `code`"

    result = processor.process(markdown)
    assert result == expected


def test_indented_placeholder_items_should_be_processed(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "  __NUM__. Indented item\n  __NUM__. Another indented"
    expected = "1. Indented item\n2. Another indented"

    result = processor.process(markdown)
    assert result == expected


def test_mixed_content_with_headings_and_lists_should_process_correctly(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = (
        "# Heading\n"
        "\n"
        "__NUM__. First item\n"
        "__NUM__. Second item\n"
        "\n"
        "Some paragraph\n"
        "\n"
        "__NUM__. Another list\n"
        "__NUM__. With items\n"
        "\n"
        "More text"
    )
    expected = (
        "# Heading\n\n1. First item\n2. Second item\n\nSome paragraph\n\n1. Another list\n2. With items\n\nMore text"
    )

    result = processor.process(markdown)
    assert result == expected


def test_regular_numbered_lists_should_remain_unchanged(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "1. First item\n2. Second item\n3. Third item"
    result = processor.process(markdown)
    assert result == markdown


def test_list_with_empty_content_should_process_correctly(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "__NUM__. \n__NUM__. Item with content\n__NUM__. "
    expected = "1. \n2. Item with content\n3. "

    result = processor.process(markdown)
    assert result == expected


def test_very_long_list_should_process_correctly(processor: NumberedListPlaceholderReplaceerPostProcessor) -> None:
    items = [f"__NUM__. Item {i}" for i in range(1, 101)]
    markdown = "\n".join(items)

    expected_items = [f"{i}. Item {i}" for i in range(1, 101)]
    expected = "\n".join(expected_items)

    result = processor.process(markdown)
    assert result == expected


def test_list_with_special_characters_should_process_correctly(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "__NUM__. Content with special chars: <>&\"'\n__NUM__. More special: @#$%^&*()"
    expected = "1. Content with special chars: <>&\"'\n2. More special: @#$%^&*()"

    result = processor.process(markdown)
    assert result == expected


def test_list_with_unicode_content_should_process_correctly(
    processor: NumberedListPlaceholderReplaceerPostProcessor,
) -> None:
    markdown = "__NUM__. Deutsch: äöüß\n__NUM__. 日本語: こんにちは\n__NUM__. Emoji: 🎉🚀"
    expected = "1. Deutsch: äöüß\n2. 日本語: こんにちは\n3. Emoji: 🎉🚀"

    result = processor.process(markdown)
    assert result == expected
