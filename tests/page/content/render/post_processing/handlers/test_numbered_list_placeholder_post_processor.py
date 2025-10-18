import pytest

from notionary.page.content.renderer.post_processing.handlers import NumberedListPlaceholderReplacerPostProcessor


@pytest.fixture
def processor() -> NumberedListPlaceholderReplacerPostProcessor:
    return NumberedListPlaceholderReplacerPostProcessor()


def test_single_level_nested_list_should_use_alphabetic(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = "__NUM__. First item\n    __NUM__. Nested item a\n    __NUM__. Nested item b\n__NUM__. Second item"
    expected = "1. First item\n    a. Nested item a\n    b. Nested item b\n2. Second item"

    result = processor.process(markdown)
    assert result == expected


def test_two_level_nested_list_should_use_roman_numerals(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. First item\n"
        "    __NUM__. Nested level 1\n"
        "        __NUM__. Nested level 2 first\n"
        "        __NUM__. Nested level 2 second\n"
        "    __NUM__. Back to level 1\n"
        "__NUM__. Second item"
    )
    expected = (
        "1. First item\n"
        "    a. Nested level 1\n"
        "        i. Nested level 2 first\n"
        "        ii. Nested level 2 second\n"
        "    b. Back to level 1\n"
        "2. Second item"
    )

    result = processor.process(markdown)
    assert result == expected


def test_three_level_nested_list_should_cycle_back_to_numeric(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. Level 0\n"
        "    __NUM__. Level 1\n"
        "        __NUM__. Level 2\n"
        "            __NUM__. Level 3 - back to numeric\n"
        "            __NUM__. Level 3 - second item"
    )
    expected = (
        "1. Level 0\n"
        "    a. Level 1\n"
        "        i. Level 2\n"
        "            1. Level 3 - back to numeric\n"
        "            2. Level 3 - second item"
    )

    result = processor.process(markdown)
    assert result == expected


def test_complex_nested_structure_matching_notion_ui(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    """Test the exact structure from the Notion UI screenshot"""
    markdown = "__NUM__. test\n    __NUM__. fest\n        __NUM__. quest\n            __NUM__. fest"
    expected = "1. test\n    a. fest\n        i. quest\n            1. fest"

    result = processor.process(markdown)
    assert result == expected


def test_jumping_back_to_top_level_should_reset_counters(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. First top\n"
        "    __NUM__. Nested a\n"
        "        __NUM__. Nested i\n"
        "__NUM__. Second top\n"
        "    __NUM__. Should be 'a' again\n"
        "        __NUM__. Should be 'i' again"
    )
    expected = (
        "1. First top\n"
        "    a. Nested a\n"
        "        i. Nested i\n"
        "2. Second top\n"
        "    a. Should be 'a' again\n"
        "        i. Should be 'i' again"
    )

    result = processor.process(markdown)
    assert result == expected


def test_jumping_from_deep_to_middle_level_should_reset_deeper_counters(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. Level 0\n"
        "    __NUM__. Level 1 - a\n"
        "        __NUM__. Level 2 - i\n"
        "        __NUM__. Level 2 - ii\n"
        "    __NUM__. Level 1 - b\n"
        "        __NUM__. Level 2 - should be i again\n"
        "        __NUM__. Level 2 - should be ii again"
    )
    expected = (
        "1. Level 0\n"
        "    a. Level 1 - a\n"
        "        i. Level 2 - i\n"
        "        ii. Level 2 - ii\n"
        "    b. Level 1 - b\n"
        "        i. Level 2 - should be i again\n"
        "        ii. Level 2 - should be ii again"
    )

    result = processor.process(markdown)
    assert result == expected


def test_multiple_items_at_each_level_should_count_correctly(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. First\n"
        "__NUM__. Second\n"
        "__NUM__. Third\n"
        "    __NUM__. Nested a\n"
        "    __NUM__. Nested b\n"
        "    __NUM__. Nested c\n"
        "        __NUM__. Deep i\n"
        "        __NUM__. Deep ii\n"
        "        __NUM__. Deep iii"
    )
    expected = (
        "1. First\n"
        "2. Second\n"
        "3. Third\n"
        "    a. Nested a\n"
        "    b. Nested b\n"
        "    c. Nested c\n"
        "        i. Deep i\n"
        "        ii. Deep ii\n"
        "        iii. Deep iii"
    )

    result = processor.process(markdown)
    assert result == expected


def test_alphabetic_continues_beyond_z(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    """Test that alphabetic numbering handles more than 26 items"""
    items = ["    __NUM__. Item" for _ in range(28)]
    markdown = "__NUM__. Top\n" + "\n".join(items)

    expected_lines = ["1. Top"]
    for i in range(1, 29):
        if i <= 26:
            letter = chr(ord("a") + i - 1)
        elif i == 27:
            letter = "aa"
        else:
            letter = "ab"
        expected_lines.append(f"    {letter}. Item")

    expected = "\n".join(expected_lines)

    result = processor.process(markdown)
    assert result == expected


def test_roman_numerals_for_common_numbers(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. Top\n"
        "    __NUM__. Level 1\n"
        "        __NUM__. i\n"
        "        __NUM__. ii\n"
        "        __NUM__. iii\n"
        "        __NUM__. iv\n"
        "        __NUM__. v\n"
        "        __NUM__. vi\n"
        "        __NUM__. vii\n"
        "        __NUM__. viii\n"
        "        __NUM__. ix\n"
        "        __NUM__. x"
    )
    expected = (
        "1. Top\n"
        "    a. Level 1\n"
        "        i. i\n"
        "        ii. ii\n"
        "        iii. iii\n"
        "        iv. iv\n"
        "        v. v\n"
        "        vi. vi\n"
        "        vii. vii\n"
        "        viii. viii\n"
        "        ix. ix\n"
        "        x. x"
    )

    result = processor.process(markdown)
    assert result == expected


def test_nested_lists_with_blank_lines_between_should_work(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. First item\n"
        "\n"
        "__NUM__. Second item\n"
        "    __NUM__. Nested a\n"
        "\n"
        "    __NUM__. Nested b\n"
        "\n"
        "__NUM__. Third item"
    )
    expected = "1. First item\n2. Second item\n    a. Nested a\n    b. Nested b\n3. Third item"

    result = processor.process(markdown)
    assert result == expected


def test_nested_lists_with_content_between_should_reset_counters(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. First list item\n"
        "    __NUM__. Nested a\n"
        "        __NUM__. Nested i\n"
        "\n"
        "Some paragraph text here\n"
        "\n"
        "__NUM__. New list starts\n"
        "    __NUM__. Should be 'a' again\n"
        "        __NUM__. Should be 'i' again"
    )
    expected = (
        "1. First list item\n"
        "    a. Nested a\n"
        "        i. Nested i\n"
        "\n"
        "Some paragraph text here\n"
        "\n"
        "1. New list starts\n"
        "    a. Should be 'a' again\n"
        "        i. Should be 'i' again"
    )

    result = processor.process(markdown)
    assert result == expected


def test_four_level_deep_nesting_should_cycle_correctly(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    """Level 4 should be alphabetic (cycling: numeric → alpha → roman → numeric → alpha)"""
    markdown = (
        "__NUM__. L0 - numeric\n"
        "    __NUM__. L1 - alpha\n"
        "        __NUM__. L2 - roman\n"
        "            __NUM__. L3 - numeric again\n"
        "                __NUM__. L4 - alpha again\n"
        "                __NUM__. L4 - second"
    )
    expected = (
        "1. L0 - numeric\n"
        "    a. L1 - alpha\n"
        "        i. L2 - roman\n"
        "            1. L3 - numeric again\n"
        "                a. L4 - alpha again\n"
        "                b. L4 - second"
    )

    result = processor.process(markdown)
    assert result == expected


def test_nested_list_with_mixed_content_and_formatting(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = (
        "__NUM__. **Bold** top item\n"
        "    __NUM__. _Italic_ nested\n"
        "        __NUM__. Item with `code`\n"
        "            __NUM__. Item with [link](url)\n"
        "__NUM__. Second top with **formatting**"
    )
    expected = (
        "1. **Bold** top item\n"
        "    a. _Italic_ nested\n"
        "        i. Item with `code`\n"
        "            1. Item with [link](url)\n"
        "2. Second top with **formatting**"
    )

    result = processor.process(markdown)
    assert result == expected


def test_eight_spaces_should_be_level_2(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    """Verify that 8 spaces = level 2 (roman numerals)"""
    markdown = "__NUM__. Level 0\n        __NUM__. This is 8 spaces - should be level 2 roman"
    expected = "1. Level 0\n        i. This is 8 spaces - should be level 2 roman"

    result = processor.process(markdown)
    assert result == expected


def test_empty_nested_items_should_process_correctly(
    processor: NumberedListPlaceholderReplacerPostProcessor,
) -> None:
    markdown = "__NUM__. Item with content\n    __NUM__. \n    __NUM__. Another with content\n        __NUM__. "
    expected = "1. Item with content\n    a. \n    b. Another with content\n        i. "

    result = processor.process(markdown)
    assert result == expected
