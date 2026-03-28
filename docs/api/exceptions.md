# Exceptions

All exceptions inherit from `NotionaryException`.
Import them from `notionary.exceptions` or from their respective subpackages.

```python
from notionary.exceptions import PageNotFound, DatabaseNotFound
```

::: notionary.exceptions.base.NotionaryException

::: notionary.page.exceptions.PageNotFound

::: notionary.database.exceptions.DatabaseNotFound

::: notionary.data_source.exceptions.DataSourceNotFound

::: notionary.file_upload.exceptions.FileNotFoundError

::: notionary.file_upload.exceptions.FilenameTooLongError

::: notionary.file_upload.exceptions.NoFileExtensionException

::: notionary.file_upload.exceptions.UnsupportedFileTypeException

::: notionary.file_upload.exceptions.UploadFailedError

::: notionary.file_upload.exceptions.UploadTimeoutError
