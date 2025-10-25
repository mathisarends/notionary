from notionary.file_upload.query.models import FileUploadQuery
from notionary.file_upload.schemas import FileUploadStatus


def test_default_values() -> None:
    query = FileUploadQuery()

    assert query.status is None
    assert query.archived is None
    assert query.page_size_limit is None
    assert query.total_results_limit is None


def test_page_size_limit_none() -> None:
    query = FileUploadQuery(page_size_limit=None)

    assert query.page_size_limit is None


def test_page_size_limit_valid_value() -> None:
    query = FileUploadQuery(page_size_limit=50)

    assert query.page_size_limit == 50


def test_page_size_limit_clips_to_max() -> None:
    query = FileUploadQuery(page_size_limit=200)

    assert query.page_size_limit == 100


def test_page_size_limit_clips_to_min() -> None:
    query = FileUploadQuery(page_size_limit=-10)

    assert query.page_size_limit == 1


def test_page_size_limit_clips_zero_to_min() -> None:
    query = FileUploadQuery(page_size_limit=0)

    assert query.page_size_limit == 1


def test_total_results_limit_none_becomes_100() -> None:
    query = FileUploadQuery(total_results_limit=None)

    assert query.total_results_limit == 100


def test_total_results_limit_valid_value() -> None:
    query = FileUploadQuery(total_results_limit=500)

    assert query.total_results_limit == 500


def test_total_results_limit_clips_to_min() -> None:
    query = FileUploadQuery(total_results_limit=-5)

    assert query.total_results_limit == 1


def test_total_results_limit_clips_zero_to_min() -> None:
    query = FileUploadQuery(total_results_limit=0)

    assert query.total_results_limit == 1


def test_serialization_with_status_only() -> None:
    query = FileUploadQuery(status=FileUploadStatus.UPLOADED)
    serialized = query.model_dump()

    assert serialized == {"status": FileUploadStatus.UPLOADED}


def test_serialization_with_archived_only() -> None:
    query = FileUploadQuery(archived=True)
    serialized = query.model_dump()

    assert serialized == {"archived": True}


def test_serialization_with_status_and_archived() -> None:
    query = FileUploadQuery(status=FileUploadStatus.PENDING, archived=False)
    serialized = query.model_dump()

    assert serialized == {"status": FileUploadStatus.PENDING, "archived": False}


def test_serialization_excludes_page_size_limit() -> None:
    query = FileUploadQuery(status=FileUploadStatus.UPLOADED, page_size_limit=50)
    serialized = query.model_dump()

    assert "page_size_limit" not in serialized
    assert serialized == {"status": FileUploadStatus.UPLOADED}


def test_serialization_excludes_total_results_limit() -> None:
    query = FileUploadQuery(status=FileUploadStatus.UPLOADED, total_results_limit=200)
    serialized = query.model_dump()

    assert "total_results_limit" not in serialized
    assert serialized == {"status": FileUploadStatus.UPLOADED}


def test_serialization_empty_when_no_status_or_archived() -> None:
    query = FileUploadQuery(page_size_limit=50, total_results_limit=200)
    serialized = query.model_dump()

    assert serialized == {}


def test_full_model_with_all_fields() -> None:
    query = FileUploadQuery(status=FileUploadStatus.FAILED, archived=True, page_size_limit=75, total_results_limit=300)

    assert query.status == FileUploadStatus.FAILED
    assert query.archived is True
    assert query.page_size_limit == 75
    assert query.total_results_limit == 300

    serialized = query.model_dump()
    assert serialized == {"status": FileUploadStatus.FAILED, "archived": True}
