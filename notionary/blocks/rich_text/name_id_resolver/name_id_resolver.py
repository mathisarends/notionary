from abc import ABC, abstractmethod


class NameIdResolver(ABC):
    @abstractmethod
    def resolve_name_to_id(self, name: str) -> str | None:
        pass

    @abstractmethod
    def resolve_id_to_name(self, id: str) -> str | None:
        pass
