# File Uploads

The `NotionFileUpload` service lets you upload files to Notion so they can be reused as page icons, covers, or file blocks. You can upload from a local path or directly from in‑memory bytes (e.g. AI‑generated images).

## Instantiating

```python
from notionary.file_upload.service import NotionFileUpload

uploader = NotionFileUpload()
```

## Single vs Multi‑Part Uploads

Uploads smaller than the Notion single‑part limit (`NOTION_SINGLE_PART_MAX_SIZE`) are sent in one request. Larger uploads are automatically split into multiple parts and each chunk is sent sequentially. You do not need to manage this logic manually – the service decides based on file size.

## Upload From Disk

```python
from pathlib import Path

response = await uploader.upload_file(Path("./images/logo.png"))
print(response.id, response.status)
```

Optionally override the filename:

```python
response = await uploader.upload_file(Path("./images/temp.png"), filename="brand.png")
```

## Upload From Bytes (e.g. AI‑Generated Content)

Useful when you generate images in memory and never write them to disk:

```python
image_bytes = generate_image_somehow()
response = await uploader.upload_from_bytes(
    file_content=image_bytes,
    filename="ai_cover.png",
    content_type="image/png",
)
print(response.id)
```

If omitted, `content_type` is guessed from the filename using Python's `mimetypes`.

## Using Uploaded Files as Page Assets

Once you have a `file_upload_id` you can attach it to pages or data sources (for icons / covers).

```python
from notionary import NotionPage

page = await NotionPage.from_id("your-page-id")

# Set icon from upload
await page.set_icon_from_file_upload(response.id)

# Set cover image from upload
await page.set_cover_image_from_file_upload(response.id)
```

Or upload directly from disk + apply:

```python
await page.set_icon_from_file(Path("./assets/icon.png"))
await page.set_cover_image_from_file(Path("./assets/cover.jpg"))
```

And from bytes:

```python
await page.set_icon_from_bytes(icon_bytes, filename="spark.png")
await page.set_cover_image_from_bytes(cover_bytes, filename="gradient.png")
```

## Using Uploaded Files for Data Sources / Databases

The same pattern works for data source or database metadata (emoji/icon/cover helpers mirror the page API where supported).

```python
from notionary import NotionDataSource

ds = await NotionDataSource.from_id("data-source-id")
await ds.set_cover_image_from_file_upload(response.id)
```

## Polling & Status

The service polls until the upload status becomes `uploaded` or `failed`. You get back a `FileUploadResponse` once complete:

```python
print(response.status)  # FileUploadStatus.UPLOADED
print(response.filename, response.content_type, response.content_length)
```

To check later:

```python
status = await uploader.get_upload_status(response.id)
```

## Listing Uploads

List all uploads (optionally filter by status or archived state):

```python
uploads = await uploader.get_uploads()
for u in uploads:
    print(u.id, u.status)
```

With a builder filter:

```python
from notionary.file_upload.query.builder import FileUploadQueryBuilder

uploads = await uploader.get_uploads(
    filter_fn=lambda b: b
        .with_uploaded_status_only()   # only UPLOADED
        .with_page_size_limit(20)      # page size 1..100
)
```

Streaming variant (memory efficient):

```python
async for upload in uploader.iter_uploads():
    print(upload.id)
```

### Query builder (details)

You can either pass a small function that configures a `FileUploadQueryBuilder` (as above), or build a `FileUploadQuery` explicitly and pass it via the `query=` argument.

Common patterns:

```python
from notionary.file_upload.query.builder import FileUploadQueryBuilder

# Only pending, not archived, limit page size
uploads = await uploader.get_uploads(
    filter_fn=lambda b: b
        .with_pending_status_only()
        .with_archived(False)
        .with_page_size_limit(50)
)

# Build a query object explicitly (e.g., only failed, total cap 60)
query = (
    FileUploadQueryBuilder()
    .with_failed_status_only()
    .with_total_results_limit(60)  # 1..100
    .build()
)
uploads = await uploader.get_uploads(query=query)

# Stream with a filter
async for u in uploader.iter_uploads(
    filter_fn=lambda b: b.with_expired_status_only()
):
    print(u.id, u.status)
```

Builder API (selected):

- `with_status(status)` or shortcuts: `with_uploaded_status_only()`, `with_pending_status_only()`, `with_failed_status_only()`, `with_expired_status_only()`
- `with_archived(bool)`
- `with_page_size_limit(n)` where 1 ≤ n ≤ 100
- `with_total_results_limit(n)` where 1 ≤ n ≤ 100
- `build()` → `FileUploadQuery`

## Error Handling

- `UploadFailedError`: a part failed to send or the final status is `failed`.
- `UploadTimeoutError`: overall upload did not complete within the configured timeout.
- Validation errors: filename too long, size exceeds configured maximum, or invalid number of parts.

Wrap calls if you need custom recovery:

```python
try:
    response = await uploader.upload_file(Path("big.zip"))
except UploadTimeoutError:
    print("Timed out – retry later")
except UploadFailedError as e:
    print("Failed:", e)
```

## Reference

`FileUploadResponse` fields:
- `id`: Identifier used when attaching as icon/cover.
- `status`: One of `pending`, `uploaded`, `failed`, `expired`.
- `filename`, `content_type`, `content_length`: Metadata you supplied or that was inferred.
- `expiry_time`: When the upload link becomes invalid (for multi‑part flows).

For attaching to blocks (e.g. file blocks) construct a `FileUploadAttachment` via `FileUploadAttachment.from_id(upload_id)` and include it in the block creation call.

!!! info "Notion API Reference"
    For the official Notion guide on files and media, see https://developers.notion.com/docs/working-with-files-and-media
