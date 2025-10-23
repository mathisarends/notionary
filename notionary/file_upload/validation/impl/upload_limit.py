from typing import TYPE_CHECKING, override

from notionary.file_upload.validation.port import FileUploadValidator

if TYPE_CHECKING:
    from notionary.user import BotUser


class FileUploadSizeValidator(FileUploadValidator):
    @override
    async def validate(self, integration: BotUser | None = None) -> None:
        from notionary.user import BotUser

        integration = integration or BotUser.from_current_integration()

        # max_file_size_in_bytes = integration.workspace_file_upload_limit_in_bytes
