from notionary.blocks.schemas import BlockCreatePayload
from notionary.page.content.parser.post_processing.port import PostProcessor


class BlockPostProcessor:
    def __init__(self) -> None:
        self._processors: list[PostProcessor] = []

    def register(self, processor: PostProcessor) -> None:
        self._processors.append(processor)

    def process(self, created_blocks: list[BlockCreatePayload]) -> list[BlockCreatePayload]:
        result = created_blocks
        for processor in self._processors:
            result = processor.process(created_blocks)
        return result
