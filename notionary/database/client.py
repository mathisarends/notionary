from notionary.database.schemas import (
    DatabaseDto,
    DatabaseUpdateDto,
)
from notionary.http.client import HttpClient
from notionary.shared.rich_text.schemas import RichText


class DatabaseHttpClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get_database(self, database_id: str) -> DatabaseDto:
        response = await self._http.get(f"databases/{database_id}")
        return DatabaseDto.model_validate(response)

    async def patch_database(
        self, database_id: str, update_database_dto: DatabaseUpdateDto
    ) -> DatabaseDto:
        update_database_dto_dict = update_database_dto.model_dump(exclude_none=True)

        response = await self._http.patch(
            f"databases/{database_id}", data=update_database_dto_dict
        )
        return DatabaseDto.model_validate(response)

    async def update_database_title(
        self, database_id: str, title: list[RichText]
    ) -> DatabaseDto:
        return await self.patch_database(database_id, DatabaseUpdateDto(title=title))

    async def update_database_description(
        self, database_id: str, description: list[RichText]
    ) -> DatabaseDto:
        return await self.patch_database(
            database_id, DatabaseUpdateDto(description=description)
        )
