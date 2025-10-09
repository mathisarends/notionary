from abc import ABC, abstractmethod


class PreProcessor(ABC):
    @abstractmethod
    def process(self, markdown_text: str) -> str:
        pass
