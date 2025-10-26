from typing import Self

from notionary.file_upload.query.models import FileUploadQuery
from notionary.file_upload.schemas import FileUploadStatus


class FileUploadQueryBuilder:
    def __init__(self, query: FileUploadQuery | None = None):
        self._query = query or FileUploadQuery()

    def with_status(self, status: FileUploadStatus) -> Self:
        self._query.status = status
        return self

    def with_uploaded_status_only(self) -> Self:
        self._query.status = FileUploadStatus.UPLOADED
        return self

    def with_pending_status_only(self) -> Self:
        self._query.status = FileUploadStatus.PENDING
        return self

    def with_failed_status_only(self) -> Self:
        self._query.status = FileUploadStatus.FAILED
        return self

    def with_expired_status_only(self) -> Self:
        self._query.status = FileUploadStatus.EXPIRED
        return self

    def with_archived(self, archived: bool) -> Self:
        self._query.archived = archived
        return self

    def with_page_size_limit(self, page_size_limit: int) -> Self:
        self._query.page_size_limit = self._validate_page_size_limit(page_size_limit)
        return self

    def _validate_page_size_limit(self, value: int) -> int:
        if not (1 <= value <= 100):
            raise ValueError(f"page_size_limit must be between 1 and 100, got {value}")
        return value

    def with_total_results_limit(self, total_results_limit: int) -> Self:
        self._query.total_results_limit = self._validate_total_results_limit(
            total_results_limit
        )
        return self

    def _validate_total_results_limit(self, value: int) -> int:
        if not (1 <= value <= 100):
            raise ValueError(
                f"total_results_limit must be between 1 and 100, got {value}"
            )
        return value

    def build(self) -> FileUploadQuery:
        return self._query
