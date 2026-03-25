from notionary.database.schemas import (
    DatabaseDto,
    DatabaseUpdateDto,
)
from notionary.http.client import NotionHttpClient
from notionary.shared.rich_text.schemas import RichText


class DatabaseHttpClient(NotionHttpClient):
    def __init__(
        self, database_id: str, token: str | None = None, timeout: int = 30
    ) -> None:
        super().__init__(token=token, timeout=timeout)
        self._database_id = database_id

    async def get_database(self) -> DatabaseDto:
        response = await self.get(f"databases/{self._database_id}")
        return DatabaseDto.model_validate(response)

    async def patch_database(
        self, update_database_dto: DatabaseUpdateDto
    ) -> DatabaseDto:
        update_database_dto_dict = update_database_dto.model_dump(exclude_none=True)

        response = await self.patch(
            f"databases/{self._database_id}", data=update_database_dto_dict
        )
        return DatabaseDto.model_validate(response)

    async def update_database_title(self, title: list[RichText]) -> DatabaseDto:
        return await self.patch_database(DatabaseUpdateDto(title=title))

    async def update_database_description(
        self, description: list[RichText]
    ) -> DatabaseDto:
        return await self.patch_database(DatabaseUpdateDto(description=description))
