import pytest

from notionary.page.content.renderer.post_processing.handlers import NumberedListPlaceholderReplacerPostProcessor
from notionary.page.content.syntax.grammar import MarkdownGrammar


@pytest.fixture
def processor() -> NumberedListPlaceholderReplacerPostProcessor:
    return NumberedListPlaceholderReplacerPostProcessor()


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def numbered_list_placeholder(markdown_grammar: MarkdownGrammar) -> str:
    return markdown_grammar.numbered_list_placeholder


def test_single_level_nested_list_should_use_alphabetic(
    processor: NumberedListPlaceholderReplacerPostProcessor,
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. First item\n"
        f"    {numbered_list_placeholder}. Nested item a\n"
        f"    {numbered_list_placeholder}. Nested item b\n"
        f"{numbered_list_placeholder}. Second item"
    )
    expected = "1. First item\n    a. Nested item a\n    b. Nested item b\n2. Second item"

    result = processor.process(markdown)
    assert result == expected


def test_two_level_nested_list_should_use_roman_numerals(
    processor: NumberedListPlaceholderReplacerPostProcessor,
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. First item\n"
        f"    {numbered_list_placeholder}. Nested level 1\n"
        f"        {numbered_list_placeholder}. Nested level 2 first\n"
        f"        {numbered_list_placeholder}. Nested level 2 second\n"
        f"    {numbered_list_placeholder}. Back to level 1\n"
        f"{numbered_list_placeholder}. Second item"
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
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. Level 0\n"
        f"    {numbered_list_placeholder}. Level 1\n"
        f"        {numbered_list_placeholder}. Level 2\n"
        f"            {numbered_list_placeholder}. Level 3 - back to numeric\n"
        f"            {numbered_list_placeholder}. Level 3 - second item"
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
    numbered_list_placeholder: str,
) -> None:
    """Test the exact structure from the Notion UI screenshot"""
    markdown = f"{numbered_list_placeholder}. test\n    {numbered_list_placeholder}. fest\n        {numbered_list_placeholder}. quest\n            {numbered_list_placeholder}. fest"
    expected = "1. test\n    a. fest\n        i. quest\n            1. fest"

    result = processor.process(markdown)
    assert result == expected


def test_jumping_back_to_top_level_should_reset_counters(
    processor: NumberedListPlaceholderReplacerPostProcessor,
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. First top\n"
        f"    {numbered_list_placeholder}. Nested a\n"
        f"        {numbered_list_placeholder}. Nested i\n"
        f"{numbered_list_placeholder}. Second top\n"
        f"    {numbered_list_placeholder}. Should be 'a' again\n"
        f"        {numbered_list_placeholder}. Should be 'i' again"
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
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. Level 0\n"
        f"    {numbered_list_placeholder}. Level 1 - a\n"
        f"        {numbered_list_placeholder}. Level 2 - i\n"
        f"        {numbered_list_placeholder}. Level 2 - ii\n"
        f"    {numbered_list_placeholder}. Level 1 - b\n"
        f"        {numbered_list_placeholder}. Level 2 - should be i again\n"
        f"        {numbered_list_placeholder}. Level 2 - should be ii again"
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
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. First\n"
        f"{numbered_list_placeholder}. Second\n"
        f"{numbered_list_placeholder}. Third\n"
        f"    {numbered_list_placeholder}. Nested a\n"
        f"    {numbered_list_placeholder}. Nested b\n"
        f"    {numbered_list_placeholder}. Nested c\n"
        f"        {numbered_list_placeholder}. Deep i\n"
        f"        {numbered_list_placeholder}. Deep ii\n"
        f"        {numbered_list_placeholder}. Deep iii"
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
    numbered_list_placeholder: str,
) -> None:
    items = [f"    {numbered_list_placeholder}. Item" for _ in range(28)]
    markdown = f"{numbered_list_placeholder}. Top\n" + "\n".join(items)

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
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. Top\n"
        f"    {numbered_list_placeholder}. Level 1\n"
        f"        {numbered_list_placeholder}. i\n"
        f"        {numbered_list_placeholder}. ii\n"
        f"        {numbered_list_placeholder}. iii\n"
        f"        {numbered_list_placeholder}. iv\n"
        f"        {numbered_list_placeholder}. v\n"
        f"        {numbered_list_placeholder}. vi\n"
        f"        {numbered_list_placeholder}. vii\n"
        f"        {numbered_list_placeholder}. viii\n"
        f"        {numbered_list_placeholder}. ix\n"
        f"        {numbered_list_placeholder}. x"
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
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. First item\n"
        "\n"
        f"{numbered_list_placeholder}. Second item\n"
        f"    {numbered_list_placeholder}. Nested a\n"
        "\n"
        f"    {numbered_list_placeholder}. Nested b\n"
        "\n"
        f"{numbered_list_placeholder}. Third item"
    )
    expected = "1. First item\n2. Second item\n    a. Nested a\n    b. Nested b\n3. Third item"

    result = processor.process(markdown)
    assert result == expected


def test_nested_lists_with_content_between_should_reset_counters(
    processor: NumberedListPlaceholderReplacerPostProcessor,
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. First list item\n"
        f"    {numbered_list_placeholder}. Nested a\n"
        f"        {numbered_list_placeholder}. Nested i\n"
        "\n"
        "Some paragraph text here\n"
        "\n"
        f"{numbered_list_placeholder}. New list starts\n"
        f"    {numbered_list_placeholder}. Should be 'a' again\n"
        f"        {numbered_list_placeholder}. Should be 'i' again"
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
    numbered_list_placeholder: str,
) -> None:
    """Level 4 should be alphabetic (cycling: numeric → alpha → roman → numeric → alpha)"""
    markdown = (
        f"{numbered_list_placeholder}. L0 - numeric\n"
        f"    {numbered_list_placeholder}. L1 - alpha\n"
        f"        {numbered_list_placeholder}. L2 - roman\n"
        f"            {numbered_list_placeholder}. L3 - numeric again\n"
        f"                {numbered_list_placeholder}. L4 - alpha again\n"
        f"                {numbered_list_placeholder}. L4 - second"
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
    numbered_list_placeholder: str,
) -> None:
    markdown = (
        f"{numbered_list_placeholder}. **Bold** top item\n"
        f"    {numbered_list_placeholder}. _Italic_ nested\n"
        f"        {numbered_list_placeholder}. Item with `code`\n"
        f"            {numbered_list_placeholder}. Item with [link](url)\n"
        f"{numbered_list_placeholder}. Second top with **formatting**"
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
    numbered_list_placeholder: str,
) -> None:
    """Verify that 8 spaces = level 2 (roman numerals)"""
    markdown = f"{numbered_list_placeholder}. Level 0\n        {numbered_list_placeholder}. This is 8 spaces - should be level 2 roman"
    expected = "1. Level 0\n        i. This is 8 spaces - should be level 2 roman"

    result = processor.process(markdown)
    assert result == expected


def test_empty_nested_items_should_process_correctly(
    processor: NumberedListPlaceholderReplacerPostProcessor,
    numbered_list_placeholder: str,
) -> None:
    markdown = f"{numbered_list_placeholder}. Item with content\n    {numbered_list_placeholder}. \n    {numbered_list_placeholder}. Another with content\n        {numbered_list_placeholder}. "
    expected = "1. Item with content\n    a. \n    b. Another with content\n        i. "

    result = processor.process(markdown)
    assert result == expected
