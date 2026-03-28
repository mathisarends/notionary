# File Uploads

Access file uploads through `notion.file_uploads`.

```python
from pathlib import Path

async with Notionary() as notion:
    result = await notion.file_uploads.upload(Path("./report.pdf"))
    result = await notion.file_uploads.upload_from_bytes(data, "chart.png")
    uploads = await notion.file_uploads.list()
```

::: notionary.file_upload.namespace.FileUploads

---

## FileUploadResponse

::: notionary.file_upload.schemas.FileUploadResponse

---

## FileUploadStatus

::: notionary.file_upload.schemas.FileUploadStatus

!!! info "Notion API Reference"
[File Uploads](https://developers.notion.com/reference/file-uploads-intro)
