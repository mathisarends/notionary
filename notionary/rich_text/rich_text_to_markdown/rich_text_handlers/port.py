from abc import ABC, abstractmethod


class RichTextHandler(ABC):
    @abstractmethod
    def handle(
        self,
    ) -> str:
        pass

    # TOOD: Implement this here
    ...
