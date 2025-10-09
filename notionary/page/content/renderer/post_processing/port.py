from abc import ABC, abstractmethod


class PostProcessor(ABC):
    @abstractmethod
    def process(self, markdown_text: str) -> str:
        pass
