import pytest

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar


@pytest.fixture
def grammar():
    return MarkdownGrammar()


def test_singleton_returns_same_instance():
    g1 = MarkdownGrammar()
    g2 = MarkdownGrammar()
    assert g1 is g2


def test_breadcrumb_pattern_matches_exact(grammar: MarkdownGrammar):
    assert grammar.breadcrumb_pattern.match("[breadcrumb]")
    assert grammar.breadcrumb_pattern.match("[BREADCRUMB]")
    assert grammar.breadcrumb_pattern.match("[breadcrumb]  ")
    assert not grammar.breadcrumb_pattern.match("[breadcrumb] text")
    assert not grammar.breadcrumb_pattern.match("text [breadcrumb]")


def test_bulleted_list_pattern_captures_indentation_and_content(
    grammar: MarkdownGrammar,
):
    match = grammar.bulleted_list_pattern.match("- item")
    assert match
    assert match.group(1) == ""
    assert match.group(2) == "item"

    match = grammar.bulleted_list_pattern.match("    - nested item")
    assert match
    assert match.group(1) == "    "
    assert match.group(2) == "nested item"

    assert not grammar.bulleted_list_pattern.match("- [ ] todo")
    assert not grammar.bulleted_list_pattern.match("- [x] done")


def test_divider_pattern_matches_three_or_more_dashes(grammar: MarkdownGrammar):
    assert grammar.divider_pattern.match("---")
    assert grammar.divider_pattern.match("-----")
    assert grammar.divider_pattern.match("  ---  ")
    assert not grammar.divider_pattern.match("--")
    assert not grammar.divider_pattern.match("--- text")


def test_numbered_list_pattern_captures_number_and_content(grammar: MarkdownGrammar):
    match = grammar.numbered_list_pattern.match("1. first item")
    assert match
    assert match.group(1) == ""
    assert match.group(2) == "1"
    assert match.group(3) == "first item"

    match = grammar.numbered_list_pattern.match("    42. nested item")
    assert match
    assert match.group(1) == "    "
    assert match.group(2) == "42"


def test_quote_pattern_matches_single_quote_mark(grammar: MarkdownGrammar):
    match = grammar.quote_pattern.match("> quote text")
    assert match
    assert match.group(1) == "quote text"

    assert not grammar.quote_pattern.match(">> double quote")


def test_table_pattern_matches_pipe_delimited_content(grammar: MarkdownGrammar):
    assert grammar.table_pattern.match("| cell 1 | cell 2 |")
    assert grammar.table_pattern.match("|a|b|")
    assert not grammar.table_pattern.match("| no closing pipe")
    assert not grammar.table_pattern.match("no pipes")


def test_table_row_pattern_matches_separator_row(grammar: MarkdownGrammar):
    assert grammar.table_row_pattern.match("| --- | --- |")
    assert grammar.table_row_pattern.match("| :--- | ---: |")
    assert grammar.table_row_pattern.match("| :---: | --- |")


def test_table_of_contents_pattern_case_insensitive(grammar: MarkdownGrammar):
    assert grammar.table_of_contents_pattern.match("[toc]")
    assert grammar.table_of_contents_pattern.match("[TOC]")
    assert grammar.table_of_contents_pattern.match("[Toc]")


def test_todo_pattern_matches_unchecked_checkbox(grammar: MarkdownGrammar):
    match = grammar.todo_pattern.match("- [ ] task")
    assert match
    assert match.group(1) == "task"

    match = grammar.todo_pattern.match("    - [ ] nested task")
    assert match


def test_todo_done_pattern_matches_checked_checkbox_case_insensitive(
    grammar: MarkdownGrammar,
):
    match = grammar.todo_done_pattern.match("- [x] done task")
    assert match
    assert match.group(1) == "done task"

    match = grammar.todo_done_pattern.match("- [X] DONE")
    assert match
    assert match.group(1) == "DONE"


def test_caption_pattern_captures_caption_text(grammar: MarkdownGrammar):
    match = grammar.caption_pattern.match("[caption] My caption")
    assert match
    assert match.group(1) == "My caption"

    assert not grammar.caption_pattern.match("[caption]")
    assert not grammar.caption_pattern.match("[caption] ")


def test_space_pattern_matches_exact(grammar: MarkdownGrammar):
    assert grammar.space_pattern.match("[space]")
    assert grammar.space_pattern.match("[space]  ")
    assert not grammar.space_pattern.match("[space] text")


def test_heading_pattern_matches_one_to_three_levels(grammar: MarkdownGrammar):
    match = grammar.heading_pattern.match("# Heading 1")
    assert match
    assert match.group(1) == "#"
    assert match.group(2) == "Heading 1"

    match = grammar.heading_pattern.match("## Heading 2")
    assert match
    assert match.group(1) == "##"

    match = grammar.heading_pattern.match("### Heading 3")
    assert match
    assert match.group(1) == "###"

    assert not grammar.heading_pattern.match("#### Heading 4")
    assert not grammar.heading_pattern.match("#No space")


def test_media_block_pattern_with_custom_url(grammar: MarkdownGrammar):
    pattern = grammar.media_block_pattern("image")
    match = pattern.search("[image](url.jpg)")
    assert match
    assert match.group(1) == "url.jpg"

    assert not pattern.search("![image](url.jpg)")


def test_url_media_block_pattern_matches_http_urls(grammar: MarkdownGrammar):
    pattern = grammar.url_media_block_pattern("video")

    match = pattern.search("[video](https://example.com/video.mp4)")
    assert match
    assert match.group(1) == "https://example.com/video.mp4"

    match = pattern.search("[video](http://example.com/video.mp4)")
    assert match


def test_code_start_pattern_captures_language(grammar: MarkdownGrammar):
    match = grammar.code_start_pattern.match("```python")
    assert match
    assert match.group(1) == "python"

    match = grammar.code_start_pattern.match("```")
    assert match
    assert match.group(1) == ""


def test_code_end_pattern_matches_closing_fence(grammar: MarkdownGrammar):
    assert grammar.code_end_pattern.match("```")
    assert grammar.code_end_pattern.match("```  ")


def test_column_pattern_matches_with_optional_ratio(grammar: MarkdownGrammar):
    match = grammar.column_pattern.search(":::column")
    assert match

    match = grammar.column_pattern.search(":::column 0.5")
    assert match
    assert match.group(1) == "0.5"

    match = grammar.column_pattern.search(":::COLUMN 1.0")
    assert match


def test_column_list_pattern_case_insensitive(grammar: MarkdownGrammar):
    assert grammar.column_list_pattern.search(":::columns")
    assert grammar.column_list_pattern.search(":::COLUMNS")
    assert grammar.column_list_pattern.search(":::column")


def test_equation_patterns_match_dollar_signs(grammar: MarkdownGrammar):
    assert grammar.equation_start_pattern.match("$$")
    assert grammar.equation_start_pattern.match("$$  ")
    assert grammar.equation_end_pattern.match("$$")


def test_toggle_pattern_captures_title(grammar: MarkdownGrammar):
    match = grammar.toggle_pattern.match("+++ Toggle title")
    assert match
    assert match.group(1) == "Toggle title"


def test_toggle_end_pattern_matches_delimiter(grammar: MarkdownGrammar):
    assert grammar.toggle_end_pattern.match("+++")
    assert grammar.toggle_end_pattern.match("+++  ")


def test_toggleable_heading_pattern_captures_level_and_content(
    grammar: MarkdownGrammar,
):
    match = grammar.toggleable_heading_pattern.match("+++ # Heading")
    assert match
    assert match.group("level") == "#"
    assert match.group(2) == "Heading"

    match = grammar.toggleable_heading_pattern.match("+++ ### Heading 3")
    assert match
    assert match.group("level") == "###"

    assert not grammar.toggleable_heading_pattern.match("+++ #### Heading 4")


def test_cached_property_caches_pattern_object(grammar: MarkdownGrammar):
    pattern1 = grammar.breadcrumb_pattern
    pattern2 = grammar.breadcrumb_pattern
    assert pattern1 is pattern2
