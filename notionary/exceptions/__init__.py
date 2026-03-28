from notionary.exceptions.base import NotionaryException

__all__ = [
    "DataSourceNotFound",
    "DatabaseNotFound",
    "EntityNotFound",
    "NoFileExtensionException",
    "NotionaryException",
    "PageNotFound",
    "UnsupportedFileTypeException",
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
        case "NoFileExtensionException":
            from notionary.file_upload.exceptions import NoFileExtensionException

            return NoFileExtensionException
        case "PageNotFound":
            from notionary.page.exceptions import PageNotFound

            return PageNotFound
        case "UnsupportedFileTypeException":
            from notionary.file_upload.exceptions import UnsupportedFileTypeException

            return UnsupportedFileTypeException
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
