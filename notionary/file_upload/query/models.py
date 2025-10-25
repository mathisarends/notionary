from pydantic import BaseModel, field_validator, model_serializer

from notionary.file_upload.schemas import FileUploadStatus


class FileUploadQuery(BaseModel):
    status: FileUploadStatus | None = None
    archived: bool | None = None

    page_size_limit: int | None = None
    total_results_limit: int | None = None

    @field_validator("page_size_limit")
    @classmethod
    def validate_page_size(cls, value: int | None) -> int | None:
        if value is None:
            return None
        return max(1, min(value, 100))

    @field_validator("total_results_limit")
    @classmethod
    def validate_total_results(cls, value: int | None) -> int:
        if value is None:
            return 100
        return max(1, value)

    @model_serializer
    def serialize_model(self) -> dict[str, str | bool | None]:
        result = {}

        if self.status is not None:
            result["status"] = self.status

        if self.archived is not None:
            result["archived"] = self.archived

        return result
