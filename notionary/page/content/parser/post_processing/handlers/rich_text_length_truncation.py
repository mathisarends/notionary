"""
Handles request limits for rich texts (see https://developers.notion.com/reference/request-limits)
"""

from typing import Any, override

from notionary.blocks.schemas import BlockCreatePayload
from notionary.page.content.parser.post_processing.port import PostProcessor
from notionary.rich_text.models import RichText, RichTextType
from notionary.utils.mixins.logging import LoggingMixin

type _NestedBlockList = BlockCreatePayload | list["_NestedBlockList"]


class RichTextLengthTruncationPostProcessor(PostProcessor, LoggingMixin):
    NOTION_MAX_LENGTH = 2000
    ELLIPSIS = "..."

    def __init__(self, max_text_length: int = NOTION_MAX_LENGTH) -> None:
        self.max_text_length = max_text_length

    @override
    def process(self, blocks: list[BlockCreatePayload]) -> list[BlockCreatePayload]:
        if not blocks:
            return blocks

        flattened_blocks = self._flatten_blocks(blocks)
        return [self._process_block(block) for block in flattened_blocks]

    def _flatten_blocks(
        self, blocks: list[_NestedBlockList]
    ) -> list[BlockCreatePayload]:
        flattened: list[BlockCreatePayload] = []

        for item in blocks:
            if isinstance(item, list):
                flattened.extend(self._flatten_blocks(item))
            else:
                flattened.append(item)

        return flattened

    def _process_block(self, block: BlockCreatePayload) -> BlockCreatePayload:
        block_copy = block.model_copy(deep=True)
        content = self._get_block_content(block_copy)

        if content is not None:
            self._truncate_content(content)

        return block_copy

    def _get_block_content(self, block: BlockCreatePayload) -> Any | None:
        content = getattr(block, block.type.value, None)

        if content is None:
            return None

        if hasattr(content, "rich_text") or hasattr(content, "children"):
            return content

        return None

    def _truncate_content(self, content: object) -> None:
        self._truncate_rich_text_fields(content)
        self._truncate_children_recursively(content)

    def _truncate_rich_text_fields(self, content: object) -> None:
        if hasattr(content, "rich_text"):
            self._truncate_rich_text_list(content.rich_text)

        if hasattr(content, "caption"):
            self._truncate_rich_text_list(content.caption)

    def _truncate_children_recursively(self, content: object) -> None:
        if not hasattr(content, "children"):
            return

        children = getattr(content, "children", None)
        if not children:
            return

        for child in children:
            self._truncate_child_content(child)

    def _truncate_child_content(self, child: Any) -> None:
        child_content = self._get_block_content(child)
        if child_content:
            self._truncate_content(child_content)

    def _truncate_rich_text_list(self, rich_text_list: list[RichText]) -> None:
        for rich_text in rich_text_list:
            if self._should_truncate(rich_text):
                self._truncate_single_rich_text(rich_text)

    def _should_truncate(self, rich_text: RichText) -> bool:
        if not self._is_text_type(rich_text):
            return False

        return len(rich_text.text.content) > self.max_text_length

    def _truncate_single_rich_text(self, rich_text: RichText) -> None:
        original_length = len(rich_text.text.content)
        rich_text.text.content = self._create_truncated_text(rich_text.text.content)

        self.logger.warning(
            "Truncating text content from %d to %d characters",
            original_length,
            self.max_text_length,
        )

    def _create_truncated_text(self, content: str) -> str:
        cutoff = self.max_text_length - len(self.ELLIPSIS)
        return content[:cutoff] + self.ELLIPSIS

    def _is_text_type(self, rich_text: RichText) -> bool:
        return (
            rich_text.type == RichTextType.TEXT
            and rich_text.text is not None
            and rich_text.text.content
        )
