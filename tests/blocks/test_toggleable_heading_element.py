import pytest
from notionary.blocks import ToggleableHeadingElement


def test_match_markdown_heading_variants():
    assert ToggleableHeadingElement.match_markdown("+# Foo")
    assert ToggleableHeadingElement.match_markdown("+## Bar")
    assert ToggleableHeadingElement.match_markdown("+### Baz")
    assert not ToggleableHeadingElement.match_markdown("## Not Toggle")
    assert not ToggleableHeadingElement.match_markdown("+#### Too deep")
    assert not ToggleableHeadingElement.match_markdown("+ Foo")  # Kein Level


@pytest.mark.parametrize(
    "text,level,content",
    [
        ("+# Section 1", 1, "Section 1"),
        ("+## Subsection", 2, "Subsection"),
        ("+### Tief", 3, "Tief"),
    ],
)
def test_markdown_to_notion_basic(text, level, content):
    block = ToggleableHeadingElement.markdown_to_notion(text)
    assert block["type"] == f"heading_{level}"
    heading = block[f"heading_{level}"]
    assert heading["is_toggleable"] is True
    assert heading["color"] == "default"
    assert isinstance(heading["rich_text"], list)
    assert heading["rich_text"][0]["plain_text"] == content


def test_markdown_to_notion_fail_cases():
    assert ToggleableHeadingElement.markdown_to_notion("## Not toggle") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#### Too deep") is None
    assert ToggleableHeadingElement.markdown_to_notion("") is None


def test_notion_to_markdown_basic():
    block = {
        "type": "heading_2",
        "heading_2": {
            "is_toggleable": True,
            "rich_text": [
                {
                    "type": "text",
                    "plain_text": "Ein Titel",
                    "text": {"content": "Ein Titel"},
                }
            ],
            "color": "default",
            "children": [],
        },
    }
    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result == "+## Ein Titel"


def test_notion_to_markdown_non_toggleable():
    block = {
        "type": "heading_2",
        "heading_2": {
            "is_toggleable": False,
            "rich_text": [
                {"type": "text", "plain_text": "Test", "text": {"content": "Test"}}
            ],
            "color": "default",
            "children": [],
        },
    }
    assert ToggleableHeadingElement.notion_to_markdown(block) is None


def test_notion_to_markdown_wrong_type():
    block = {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "plain_text": "Test", "text": {"content": "Test"}}
            ]
        },
    }
    assert ToggleableHeadingElement.notion_to_markdown(block) is None


@pytest.mark.parametrize("level", [1, 2, 3])
def test_roundtrip(level):
    content = f"Ein Toggle Level {level}"
    md = f'+{"#"*level} {content}'
    block = ToggleableHeadingElement.markdown_to_notion(md)
    out = ToggleableHeadingElement.notion_to_markdown(block)
    assert out == md


def test_pipe_content_detection():
    assert ToggleableHeadingElement._extract_pipe_content("| abc") == "abc"
    assert ToggleableHeadingElement._extract_pipe_content("|   Mehr   ") == "Mehr   "
    assert ToggleableHeadingElement._extract_pipe_content("kein pipe") is None


def test_multiline_nested_content_extraction():
    lines = [
        "+## Main Toggle",
        "| Line 1",
        "| Line 2",
        "",
        "| Line 3",
        "+# Next Section",
    ]
    nested, next_idx = ToggleableHeadingElement._extract_nested_content(lines, 1)
    assert nested == ["Line 1", "Line 2", "", "Line 3"]
    assert next_idx == 5  # bis zur nächsten Toggle-Section


def test_extract_nested_content_stops_on_new_toggle():
    lines = [
        "+# Outer",
        "| A",
        "+## Inner",  # This should not be included as nested
    ]
    nested, next_idx = ToggleableHeadingElement._extract_nested_content(lines, 1)
    assert nested == ["A"]
    assert next_idx == 2


def test_process_nested_content_callback_usage():
    # This test simulates that children blocks are added via the callback
    block = ToggleableHeadingElement.markdown_to_notion("+## Outer")

    def dummy_processor(text):
        return [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "plain_text": text, "text": {"content": text}}
                    ]
                },
            }
        ]

    ToggleableHeadingElement._process_nested_content(
        block, ["Dies ist Child"], dummy_processor
    )
    heading = block["heading_2"]
    assert heading["children"][0]["type"] == "paragraph"
    assert (
        heading["children"][0]["paragraph"]["rich_text"][0]["plain_text"]
        == "Dies ist Child"
    )


def test_is_multiline():
    assert ToggleableHeadingElement.is_multiline() is True


def test_llm_prompt_content():
    content = ToggleableHeadingElement.get_llm_prompt_content()
    assert content.syntax.strip().startswith("+#")
    assert "pipe prefix" in content.syntax
