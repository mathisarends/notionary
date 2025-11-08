# Listing uploads & query builder

Fetch uploads with optional filtering, limits, and streaming.

## Simple listing

```python
uploads = await uploader.get_uploads()
for u in uploads:
	print(u.id, u.status)
```

## Build a query config

```python
from notionary import FileUploadQueryBuilder

query = (
	FileUploadQueryBuilder()
	.with_uploaded_status_only()
	.with_page_size_limit(20)
	.build()
)
uploads = await uploader.get_uploads(query=query)
```

Another example:

```python
query = (
	FileUploadQueryBuilder()
	.with_failed_status_only()
	.with_total_results_limit(60)  # 1..100
	.build()
)
uploads = await uploader.get_uploads(query=query)
```

## Streaming (memory‑efficient)

```python
# No filter
async for upload in uploader.iter_uploads():
	print(upload.id)

# With query config
query = FileUploadQueryBuilder().with_expired_status_only().build()
async for upload in uploader.iter_uploads(query=query):
	print(upload.id)
```

## Builder API Reference

| Method | Purpose | Parameters / Allowed | Default / Effect |
|--------|---------|----------------------|------------------|
| `with_status(status)` | Set an explicit status filter | `status` ∈ {`UPLOADED`, `PENDING`, `FAILED`, `EXPIRED`} | No status filter if omitted |
| `with_uploaded_status_only()` | Convenience: only uploaded files | – | Sets status = `UPLOADED` |
| `with_pending_status_only()` | Convenience: only pending uploads | – | Sets status = `PENDING` |
| `with_failed_status_only()` | Convenience: only failed uploads | – | Sets status = `FAILED` |
| `with_expired_status_only()` | Convenience: only expired uploads | – | Sets status = `EXPIRED` |
| `with_archived(archived: bool)` | Include/exclude archived uploads | `archived` = `True` or `False` | If omitted, archived state not sent (server default) |
| `with_page_size_limit(n)` | Set per-page size when paginating | Integer 1–100 (validated & clamped) | If omitted, client/server default page size applies |
| `with_total_results_limit(n)` | Soft cap on total collected results | Integer 1–100 (validated; >100 becomes 100 via model) | If omitted, internal default (100) used for iteration |
| `build()` | Produce immutable query object | – | Returns `FileUploadQuery` used by service |

Notes:
1. If you don’t call `with_status` or a shortcut, all statuses are considered.
2. `page_size_limit` and `total_results_limit` are client-side controls; only `status` and `archived` are serialized to the request payload.
3. Use smaller `page_size_limit` for low-memory environments; use `total_results_limit` to prevent runaway aggregation.
