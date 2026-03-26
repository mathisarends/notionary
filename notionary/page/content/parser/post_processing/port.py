from abc import ABC, abstractmethod

from notionary.page.blocks.schemas import BlockCreatePayload


class PostProcessor(ABC):
    @abstractmethod
    def process(self, blocks: list[BlockCreatePayload]) -> list[BlockCreatePayload]:
        pass
