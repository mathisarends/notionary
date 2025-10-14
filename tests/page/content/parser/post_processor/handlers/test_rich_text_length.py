import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText, RichTextType
from notionary.blocks.schemas import (
    CodeData,
    CreateCalloutBlock,
    CreateCalloutData,
    CreateCodeBlock,
    CreateDividerBlock,
    CreateParagraphBlock,
    CreateQuoteBlock,
    CreateQuoteData,
    DividerData,
    ParagraphData,
)
from notionary.page.content.parser.post_processing.handlers.rich_text_length import (
    RichTextLengthTruncationPostProcessor,
)


@pytest.fixture
def processor() -> RichTextLengthTruncationPostProcessor:
    return RichTextLengthTruncationPostProcessor()


def create_rich_text(content: str) -> RichText:
    return RichText.from_plain_text(content)


def test_empty_blocks_should_return_empty(processor: RichTextLengthTruncationPostProcessor) -> None:
    result = processor.process([])
    assert result == []


def test_short_text_should_remain_unchanged(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateParagraphBlock(
        type=BlockType.PARAGRAPH,
        paragraph=ParagraphData(rich_text=[create_rich_text("Short text")]),
    )

    result = processor.process([block])

    assert result[0].paragraph.rich_text[0].text.content == "Short text"


def test_text_over_limit_should_be_truncated(processor: RichTextLengthTruncationPostProcessor) -> None:
    long_text = "x" * 2500
    block = CreateParagraphBlock(
        type=BlockType.PARAGRAPH,
        paragraph=ParagraphData(rich_text=[create_rich_text(long_text)]),
    )

    result = processor.process([block])

    assert len(result[0].paragraph.rich_text[0].text.content) == 2000


def test_multiple_blocks_processed_independently(processor: RichTextLengthTruncationPostProcessor) -> None:
    blocks = [
        CreateParagraphBlock(
            type=BlockType.PARAGRAPH,
            paragraph=ParagraphData(rich_text=[create_rich_text("x" * 2500)]),
        ),
        CreateParagraphBlock(
            type=BlockType.PARAGRAPH,
            paragraph=ParagraphData(rich_text=[create_rich_text("short")]),
        ),
        CreateParagraphBlock(
            type=BlockType.PARAGRAPH,
            paragraph=ParagraphData(rich_text=[create_rich_text("y" * 3000)]),
        ),
    ]

    result = processor.process(blocks)

    assert len(result[0].paragraph.rich_text[0].text.content) == 2000
    assert result[1].paragraph.rich_text[0].text.content == "short"
    assert len(result[2].paragraph.rich_text[0].text.content) == 2000


def test_multiple_rich_texts_in_block_truncated_individually(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateParagraphBlock(
        type=BlockType.PARAGRAPH,
        paragraph=ParagraphData(
            rich_text=[
                create_rich_text("x" * 2500),
                create_rich_text("short"),
                create_rich_text("y" * 3000),
            ]
        ),
    )

    result = processor.process([block])

    assert len(result[0].paragraph.rich_text[0].text.content) == 2000
    assert result[0].paragraph.rich_text[1].text.content == "short"
    assert len(result[0].paragraph.rich_text[2].text.content) == 2000


def test_caption_should_be_truncated(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateCodeBlock(
        type=BlockType.CODE,
        code=CodeData(
            rich_text=[create_rich_text("print('hello')")],
            caption=[create_rich_text("x" * 2500)],
        ),
    )

    result = processor.process([block])

    assert len(result[0].code.caption[0].text.content) == 2000
    assert result[0].code.rich_text[0].text.content == "print('hello')"


def test_children_processed_recursively(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateCalloutBlock(
        type=BlockType.CALLOUT,
        callout=CreateCalloutData(
            rich_text=[create_rich_text("a" * 2500)],
            children=[
                CreateQuoteBlock(
                    type=BlockType.QUOTE,
                    quote=CreateQuoteData(
                        rich_text=[create_rich_text("b" * 3000)],
                        children=[
                            CreateParagraphBlock(
                                type=BlockType.PARAGRAPH,
                                paragraph=ParagraphData(rich_text=[create_rich_text("c" * 2500)]),
                            )
                        ],
                    ),
                )
            ],
        ),
    )

    result = processor.process([block])

    assert len(result[0].callout.rich_text[0].text.content) == 2000
    assert len(result[0].callout.children[0].quote.rich_text[0].text.content) == 2000
    assert len(result[0].callout.children[0].quote.children[0].paragraph.rich_text[0].text.content) == 2000


def test_non_text_types_ignored(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateParagraphBlock(
        type=BlockType.PARAGRAPH,
        paragraph=ParagraphData(
            rich_text=[
                RichText.equation_inline("x^2"),
                RichText.mention_user("user-123"),
                create_rich_text("x" * 2500),
            ]
        ),
    )

    result = processor.process([block])

    assert result[0].paragraph.rich_text[0].type == RichTextType.EQUATION
    assert result[0].paragraph.rich_text[1].type == RichTextType.MENTION
    assert len(result[0].paragraph.rich_text[2].text.content) == 2000


def test_blocks_without_rich_text_unchanged(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateDividerBlock(type=BlockType.DIVIDER, divider=DividerData())

    result = processor.process([block])

    assert len(result) == 1
    assert result[0].type == BlockType.DIVIDER


def test_original_block_not_modified(processor: RichTextLengthTruncationPostProcessor) -> None:
    original_block = CreateParagraphBlock(
        type=BlockType.PARAGRAPH,
        paragraph=ParagraphData(rich_text=[create_rich_text("x" * 2500)]),
    )

    processor.process([original_block])

    assert len(original_block.paragraph.rich_text[0].text.content) == 2500


def test_nested_list_structure_flattened(processor: RichTextLengthTruncationPostProcessor) -> None:
    blocks = [
        CreateParagraphBlock(
            type=BlockType.PARAGRAPH,
            paragraph=ParagraphData(rich_text=[create_rich_text("x" * 2500)]),
        ),
        [
            CreateParagraphBlock(
                type=BlockType.PARAGRAPH,
                paragraph=ParagraphData(rich_text=[create_rich_text("y" * 2500)]),
            ),
            [
                CreateParagraphBlock(
                    type=BlockType.PARAGRAPH,
                    paragraph=ParagraphData(rich_text=[create_rich_text("z" * 2500)]),
                )
            ],
        ],
    ]

    result = processor.process(blocks)

    assert len(result) == 3
    assert all(len(block.paragraph.rich_text[0].text.content) == 2000 for block in result)


def test_empty_rich_text_list_should_be_handled(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateParagraphBlock(
        type=BlockType.PARAGRAPH,
        paragraph=ParagraphData(rich_text=[]),
    )

    result = processor.process([block])

    assert len(result) == 1
    assert result[0].paragraph.rich_text == []


def test_mixed_empty_and_filled_rich_text_lists(processor: RichTextLengthTruncationPostProcessor) -> None:
    blocks = [
        CreateParagraphBlock(
            type=BlockType.PARAGRAPH,
            paragraph=ParagraphData(rich_text=[]),
        ),
        CreateParagraphBlock(
            type=BlockType.PARAGRAPH,
            paragraph=ParagraphData(rich_text=[create_rich_text("x" * 2500)]),
        ),
        CreateParagraphBlock(
            type=BlockType.PARAGRAPH,
            paragraph=ParagraphData(rich_text=[]),
        ),
    ]

    result = processor.process(blocks)

    assert len(result) == 3
    assert result[0].paragraph.rich_text == []
    assert len(result[1].paragraph.rich_text[0].text.content) == 2000
    assert result[2].paragraph.rich_text == []


def test_empty_caption_should_be_handled(processor: RichTextLengthTruncationPostProcessor) -> None:
    block = CreateCodeBlock(
        type=BlockType.CODE,
        code=CodeData(
            rich_text=[create_rich_text("print('hello')")],
            caption=[],
        ),
    )

    result = processor.process([block])

    assert result[0].code.caption == []
    assert result[0].code.rich_text[0].text.content == "print('hello')"
