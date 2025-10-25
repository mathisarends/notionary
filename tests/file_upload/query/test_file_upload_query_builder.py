import pytest

from notionary.file_upload.query import FileUploadQueryBuilder
from notionary.file_upload.query.models import FileUploadQuery
from notionary.file_upload.schemas import FileUploadStatus


def test_with_status() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_status(FileUploadStatus.UPLOADED).build()

    assert query.status == FileUploadStatus.UPLOADED


def test_with_status_uploaded() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_uploaded_status_only().build()

    assert query.status == FileUploadStatus.UPLOADED


def test_with_status_pending() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_pending_status_only().build()

    assert query.status == FileUploadStatus.PENDING


def test_with_status_failed() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_failed_status_only().build()

    assert query.status == FileUploadStatus.FAILED


def test_with_status_expired() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_expired_status_only().build()

    assert query.status == FileUploadStatus.EXPIRED


def test_with_archived() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_archived(True).build()

    assert query.archived is True


def test_with_page_size_limit() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_page_size_limit(50).build()

    assert query.page_size_limit == 50


def test_with_page_size_limit_raises_on_too_large() -> None:
    builder = FileUploadQueryBuilder()

    with pytest.raises(ValueError, match="page_size_limit must be between 1 and 100, got 200"):
        builder.with_page_size_limit(200)


def test_with_page_size_limit_raises_on_too_small() -> None:
    builder = FileUploadQueryBuilder()

    with pytest.raises(ValueError, match="page_size_limit must be between 1 and 100, got -10"):
        builder.with_page_size_limit(-10)


def test_with_page_size_limit_raises_on_zero() -> None:
    builder = FileUploadQueryBuilder()

    with pytest.raises(ValueError, match="page_size_limit must be between 1 and 100, got 0"):
        builder.with_page_size_limit(0)


def test_with_total_results_limit() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.with_total_results_limit(50).build()

    assert query.total_results_limit == 50


def test_with_total_results_limit_raises_on_too_large() -> None:
    builder = FileUploadQueryBuilder()

    with pytest.raises(ValueError, match="total_results_limit must be between 1 and 100, got 200"):
        builder.with_total_results_limit(200)


def test_with_total_results_limit_raises_on_too_small() -> None:
    builder = FileUploadQueryBuilder()

    with pytest.raises(ValueError, match="total_results_limit must be between 1 and 100, got -5"):
        builder.with_total_results_limit(-5)


def test_with_total_results_limit_raises_on_zero() -> None:
    builder = FileUploadQueryBuilder()

    with pytest.raises(ValueError, match="total_results_limit must be between 1 and 100, got 0"):
        builder.with_total_results_limit(0)


def test_chaining_multiple_methods() -> None:
    builder = FileUploadQueryBuilder()
    query = (
        builder.with_uploaded_status_only()
        .with_archived(False)
        .with_page_size_limit(25)
        .with_total_results_limit(50)
        .build()
    )

    assert query.status == FileUploadStatus.UPLOADED
    assert query.archived is False
    assert query.page_size_limit == 25
    assert query.total_results_limit == 50


def test_builder_with_existing_query() -> None:
    existing_query = FileUploadQuery(status=FileUploadStatus.PENDING, archived=True)

    builder = FileUploadQueryBuilder(existing_query)
    query = builder.with_uploaded_status_only().build()

    assert query.status == FileUploadStatus.UPLOADED
    assert query.archived is True


def test_default_query_values() -> None:
    builder = FileUploadQueryBuilder()
    query = builder.build()

    assert query.status is None
    assert query.archived is None
    assert query.page_size_limit is None
    assert query.total_results_limit is None
