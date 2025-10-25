from typing import Self

from notionary.file_upload.query.models import FileUploadQuery
from notionary.file_upload.schemas import FileUploadStatus


class FileUploadQueryBuilder:
    def __init__(self, query: FileUploadQuery | None = None):
        self._query = query or FileUploadQuery()

    def with_status(self, status: FileUploadStatus) -> Self:
        self._query.status = status
        return self

    def with_archived(self, archived: bool) -> Self:
        self._query.archived = archived
        return self

    def with_page_size_limit(self, page_size_limit: int) -> Self:
        self._query.page_size_limit = page_size_limit
        return self

    def with_total_results_limit(self, total_results_limit) -> Self:
        self._query.total_results_limit = total_results_limit
        return self

    def build(self) -> FileUploadQuery:
        return self._query
