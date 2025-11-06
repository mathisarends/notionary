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


def test_bold_pattern_matches_double_asterisks(grammar: MarkdownGrammar):
    match = grammar.bold_pattern.search("**bold text**")
    assert match
    assert match.group(1) == "bold text"

    match = grammar.bold_pattern.search("start **bold** end")
    assert match
    assert match.group(1) == "bold"

    assert not grammar.bold_pattern.search("*single asterisk*")


def test_italic_pattern_matches_single_asterisk(grammar: MarkdownGrammar):
    match = grammar.italic_pattern.search("*italic text*")
    assert match
    assert match.group(1) == "italic text"

    match = grammar.italic_pattern.search("start *italic* end")
    assert match
    assert match.group(1) == "italic"


def test_italic_underscore_pattern_matches_underscores(grammar: MarkdownGrammar):
    match = grammar.italic_underscore_pattern.search("_italic text_")
    assert match
    assert match.group(1) == "italic text"

    match = grammar.italic_underscore_pattern.search("start _italic_ end")
    assert match
    assert match.group(1) == "italic"

    # Pattern will match greedily, so this actually matches
    match = grammar.italic_underscore_pattern.search("_underscore_text")
    assert match


def test_underline_pattern_matches_double_underscores(grammar: MarkdownGrammar):
    match = grammar.underline_pattern.search("__underlined text__")
    assert match
    assert match.group(1) == "underlined text"

    match = grammar.underline_pattern.search("start __underline__ end")
    assert match
    assert match.group(1) == "underline"


def test_strikethrough_pattern_matches_double_tildes(grammar: MarkdownGrammar):
    match = grammar.strikethrough_pattern.search("~~strikethrough~~")
    assert match
    assert match.group(1) == "strikethrough"

    match = grammar.strikethrough_pattern.search("start ~~strike~~ end")
    assert match
    assert match.group(1) == "strike"


def test_inline_code_pattern_matches_backticks(grammar: MarkdownGrammar):
    match = grammar.inline_code_pattern.search("`code snippet`")
    assert match
    assert match.group(1) == "code snippet"

    match = grammar.inline_code_pattern.search("text `inline code` more")
    assert match
    assert match.group(1) == "inline code"


def test_link_pattern_matches_markdown_links(grammar: MarkdownGrammar):
    match = grammar.link_pattern.search("[Google](https://google.com)")
    assert match
    assert match.group(1) == "Google"
    assert match.group(2) == "https://google.com"

    match = grammar.link_pattern.search("text [link](url) more")
    assert match
    assert match.group(1) == "link"
    assert match.group(2) == "url"


def test_inline_equation_pattern_matches_dollar_signs(grammar: MarkdownGrammar):
    match = grammar.inline_equation_pattern.search("$E=mc^2$")
    assert match
    assert match.group(1) == "E=mc^2"

    match = grammar.inline_equation_pattern.search("formula $a+b=c$ here")
    assert match
    assert match.group(1) == "a+b=c"


def test_color_pattern_matches_color_syntax(grammar: MarkdownGrammar):
    match = grammar.color_pattern.search("(red:text)")
    assert match
    assert match.group(1) == "red"
    assert match.group(2) == "text"

    match = grammar.color_pattern.search("some (blue:colored) text")
    assert match
    assert match.group(1) == "blue"
    assert match.group(2) == "colored"


def test_page_mention_pattern_captures_page_name(grammar: MarkdownGrammar):
    match = grammar.page_mention_pattern.search("@page[Page Name]")
    assert match
    assert match.group(1) == "Page Name"

    match = grammar.page_mention_pattern.search("text @page[My Page] more")
    assert match
    assert match.group(1) == "My Page"


def test_database_mention_pattern_captures_database_name(grammar: MarkdownGrammar):
    match = grammar.database_mention_pattern.search("@database[DB Name]")
    assert match
    assert match.group(1) == "DB Name"


def test_datasource_mention_pattern_captures_datasource_name(grammar: MarkdownGrammar):
    match = grammar.datasource_mention_pattern.search("@datasource[DS Name]")
    assert match
    assert match.group(1) == "DS Name"


def test_user_mention_pattern_captures_user_name(grammar: MarkdownGrammar):
    match = grammar.user_mention_pattern.search("@user[John Doe]")
    assert match
    assert match.group(1) == "John Doe"


def test_date_mention_pattern_captures_date(grammar: MarkdownGrammar):
    match = grammar.date_mention_pattern.search("@date[2024-01-15]")
    assert match
    assert match.group(1) == "2024-01-15"


def test_synced_block_pattern_matches_triple_arrows(grammar: MarkdownGrammar):
    match = grammar.synced_block_pattern.match(">>> Synced Block ID")
    assert match
    assert match.group(1) == "Synced Block ID"

    match = grammar.synced_block_pattern.match(">>> 12345")
    assert match
    assert match.group(1) == "12345"

    assert not grammar.synced_block_pattern.match(">> Two arrows")
    assert not grammar.synced_block_pattern.match(">>>No space")


def test_delimiter_properties_return_correct_strings(grammar: MarkdownGrammar):
    assert grammar.breadcrumb_delimiter == "[breadcrumb]"
    assert grammar.bulleted_list_delimiter == "- "
    assert grammar.divider_delimiter == "---"
    assert grammar.numbered_list_delimiter == "1. "
    assert grammar.quote_delimiter == "> "
    assert grammar.table_delimiter == "|"
    assert grammar.table_of_contents_delimiter == "[toc]"
    assert grammar.todo_delimiter == "- [ ]"
    assert grammar.todo_done_delimiter == "- [x]"
    assert grammar.caption_delimiter == "[caption]"
    assert grammar.space_delimiter == "[space]"
    assert grammar.heading_delimiter == "#"
    assert grammar.column_delimiter == ":::"
    assert grammar.toggle_delimiter == "+++"
    assert grammar.code_delimiter == "```"
    assert grammar.equation_delimiter == "$$"
    assert grammar.callout_delimiter == "[callout]"
    assert grammar.media_end_delimiter == ")"
    assert grammar.synced_block_delimiter == ">>>"


def test_mention_delimiter_properties_return_correct_strings(grammar: MarkdownGrammar):
    assert grammar.page_mention_prefix == "@page["
    assert grammar.database_mention_prefix == "@database["
    assert grammar.datasource_mention_prefix == "@datasource["
    assert grammar.user_mention_prefix == "@user["
    assert grammar.date_mention_prefix == "@date["
    assert grammar.mention_suffix == "]"


def test_rich_text_delimiter_properties_return_correct_strings(
    grammar: MarkdownGrammar,
):
    assert grammar.link_prefix == "["
    assert grammar.link_middle == "]("
    assert grammar.link_suffix == ")"
    assert grammar.code_wrapper == "`"
    assert grammar.strikethrough_wrapper == "~~"
    assert grammar.italic_wrapper == "*"
    assert grammar.underline_wrapper == "__"
    assert grammar.bold_wrapper == "**"
    assert grammar.color_prefix == "=={"
    assert grammar.color_middle == "}"
    assert grammar.color_suffix == "=="
    assert grammar.inline_equation_wrapper == "$"
    assert grammar.background_color_wrapper == "=="


def test_configuration_properties_return_correct_values(grammar: MarkdownGrammar):
    assert grammar.spaces_per_nesting_level == 4
    assert grammar.numbered_list_placeholder == "__NUM__"


def test_callout_pattern_captures_emoji_and_text(grammar: MarkdownGrammar):
    match = grammar.callout_pattern.search('[callout](😀 "Important")')
    assert match
    assert match.group(1) == "😀"
    assert match.group(2) == "Important"


def test_callout_pattern_alternative_format(grammar: MarkdownGrammar):
    match = grammar.callout_pattern.search('[callout] Important "Info"')
    assert match


def test_media_block_pattern_does_not_match_image_syntax(grammar: MarkdownGrammar):
    pattern = grammar.media_block_pattern("video")
    assert not pattern.search("![video](url.mp4)")


def test_url_media_block_pattern_requires_protocol(grammar: MarkdownGrammar):
    pattern = grammar.url_media_block_pattern("image")

    assert pattern.search("[image](https://example.com/pic.jpg)")
    assert pattern.search("[image](http://example.com/pic.jpg)")
    assert not pattern.search("[image](example.com/pic.jpg)")


def test_column_end_pattern_matches_delimiter_on_line(grammar: MarkdownGrammar):
    assert grammar.column_end_pattern.search(":::")
    # Pattern uses ^ anchor with MULTILINE, spaces after are allowed
    assert grammar.column_end_pattern.search(":::\n")


def test_column_list_end_pattern_matches_delimiter(grammar: MarkdownGrammar):
    assert grammar.column_list_end_pattern.search(":::")


def test_callout_end_pattern_matches_closing_paren(grammar: MarkdownGrammar):
    assert grammar.callout_end_pattern.search(")")


def test_media_end_pattern_matches_closing_paren(grammar: MarkdownGrammar):
    assert grammar.media_end_pattern.search(")")


def test_toggleable_heading_end_pattern_matches_delimiter(grammar: MarkdownGrammar):
    assert grammar.toggleable_heading_end_pattern.match("+++")
    assert grammar.toggleable_heading_end_pattern.match("+++  ")
