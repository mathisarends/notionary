from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.database.schemas import (
    NotionDatabaseDto,
    NotionDatabaseUpdateDto,
)
from notionary.http.http_client import NotionHttpClient


class NotionDatabaseHttpClient(NotionHttpClient):
    def __init__(self, database_id: str, timeout: int = 30) -> None:
        super().__init__(timeout)
        self._database_id = database_id

    async def get_database(self) -> NotionDatabaseDto:
        response = await self.get(f"databases/{self._database_id}")
        return NotionDatabaseDto.model_validate(response)

    async def patch_database(self, update_database_dto: NotionDatabaseUpdateDto) -> NotionDatabaseDto:
        update_database_dto_dict = update_database_dto.model_dump(exclude_none=True)

        response = await self.patch(f"databases/{self._database_id}", data=update_database_dto_dict)
        return NotionDatabaseDto.model_validate(response)

    async def update_database_title(self, title: str) -> NotionDatabaseDto:
        from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter

        markdown_rich_text_formatter = MarkdownRichTextConverter()
        database_rich_text = await markdown_rich_text_formatter.to_rich_text(title)

        database_title_update_dto = NotionDatabaseUpdateDto(title=database_rich_text)
        return await self.patch_database(database_title_update_dto)

    async def update_database_description(self, description: str) -> str:
        from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter

        markdown_to_rich_text_converter = MarkdownRichTextConverter()
        rich_text_description = await markdown_to_rich_text_converter.to_rich_text(description)

        database_description_update_dto = NotionDatabaseUpdateDto(description=rich_text_description)
        update_database_response = await self.patch_database(database_description_update_dto)

        rich_text_to_markdown_converter = RichTextToMarkdownConverter()
        return await rich_text_to_markdown_converter.to_markdown(update_database_response.description)
