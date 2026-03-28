from notionary.exceptions.base import NotionaryException

__all__ = [
    "DataSourceNotFound",
    "DatabaseNotFound",
    "EntityNotFound",
    "FileNotFoundError",
    "FilenameTooLongError",
    "NoFileExtensionException",
    "NotionaryException",
    "PageNotFound",
    "ResourceNotFound",
    "UnsupportedFileTypeException",
    "UploadFailedError",
    "UploadTimeoutError",
]


def __getattr__(name: str):
    match name:
        case "DataSourceNotFound":
            from notionary.data_source.exceptions import DataSourceNotFound

            return DataSourceNotFound
        case "DatabaseNotFound":
            from notionary.database.exceptions import DatabaseNotFound

            return DatabaseNotFound
        case "EntityNotFound":
            from notionary.shared.exceptions import EntityNotFound

            return EntityNotFound
        case "FilenameTooLongError":
            from notionary.file_upload.exceptions import FilenameTooLongError

            return FilenameTooLongError
        case "FileNotFoundError":
            from notionary.file_upload.exceptions import FileNotFoundError

            return FileNotFoundError
        case "NoFileExtensionException":
            from notionary.file_upload.exceptions import NoFileExtensionException

            return NoFileExtensionException
        case "PageNotFound":
            from notionary.page.exceptions import PageNotFound

            return PageNotFound
        case "ResourceNotFound":
            from notionary.workspace.exceptions import ResourceNotFound

            return ResourceNotFound
        case "UnsupportedFileTypeException":
            from notionary.file_upload.exceptions import UnsupportedFileTypeException

            return UnsupportedFileTypeException
        case "UploadFailedError":
            from notionary.file_upload.exceptions import UploadFailedError

            return UploadFailedError
        case "UploadTimeoutError":
            from notionary.file_upload.exceptions import UploadTimeoutError

            return UploadTimeoutError
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
