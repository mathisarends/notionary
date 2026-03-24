from abc import ABC, abstractmethod


class FileUploadValidator(ABC):
    @abstractmethod
    async def validate(self) -> None:
        pass
