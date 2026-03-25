from notionary.data_source.exceptions import (
    DataSourceNotFound,
    DataSourcePropertyNotFound,
    DataSourcePropertyTypeError,
)
from notionary.database.exceptions import DatabaseNotFound
from notionary.exceptions.base import NotionaryException
from notionary.file_upload.exceptions import (
    FileSizeException,
    NoFileExtensionException,
    UnsupportedFileTypeException,
)
from notionary.http.exceptions import (
    NotionAuthenticationError,
    NotionConnectionError,
    NotionError,
    NotionNotFoundError,
    NotionRateLimitError,
    NotionServerError,
    NotionValidationError,
)
from notionary.page.content.exceptions import (
    InsufficientColumnsError,
    InvalidColumnRatioSumError,
    UnsupportedVideoFormatError,
)
from notionary.page.exceptions import (
    AccessPagePropertyWithoutDataSourceError,
    PageNotFound,
    PagePropertyNotFoundError,
    PagePropertyTypeError,
)
from notionary.shared.exceptions import EntityNotFound
from notionary.user.exceptions import NoUsersInWorkspace, UserNotFound

NotionApiError = NotionError
NotionResourceNotFoundError = NotionNotFoundError

__all__ = [
    "AccessPagePropertyWithoutDataSourceError",
    "DataSourceNotFound",
    "DataSourcePropertyNotFound",
    "DataSourcePropertyTypeError",
    "DatabaseNotFound",
    "EntityNotFound",
    "FileSizeException",
    "InsufficientColumnsError",
    "InvalidColumnRatioSumError",
    "NoFileExtensionException",
    "NoUsersInWorkspace",
    "NotionApiError",
    "NotionAuthenticationError",
    "NotionConnectionError",
    "NotionRateLimitError",
    "NotionResourceNotFoundError",
    "NotionServerError",
    "NotionValidationError",
    "NotionaryException",
    "PageNotFound",
    "PagePropertyNotFoundError",
    "PagePropertyTypeError",
    "UnsupportedFileTypeException",
    "UnsupportedVideoFormatError",
    "UserNotFound",
]
