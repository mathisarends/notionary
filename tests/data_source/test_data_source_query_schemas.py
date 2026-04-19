import pytest
from pydantic import ValidationError

from notionary.data_source.query.filters import (
    CheckboxCondition,
    CheckboxFilter,
    CompoundFilter,
    DateCondition,
    DateFilter,
    FilesCondition,
    FilesFilter,
    MultiSelectCondition,
    MultiSelectFilter,
    NumberCondition,
    NumberFilter,
    PeopleCondition,
    PeopleFilter,
    RichTextFilter,
    SelectCondition,
    SelectFilter,
    StatusCondition,
    StatusFilter,
    TextCondition,
    TimestampFilter,
    TimestampType,
    UniqueIdFilter,
    VerificationCondition,
    VerificationFilter,
    VerificationStatus,
)
from notionary.data_source.query.sorts import (
    PropertySort,
    SortDirection,
    TimestampSort,
)
from notionary.data_source.schemas import QueryDataSourceRequest, QueryResultType


class TestCheckboxFilter:
    def test_serialize_equals_true(self) -> None:
        f = CheckboxFilter(property="Done", checkbox=CheckboxCondition(equals=True))
        result = f.model_dump(mode="json")
        assert result == {"property": "Done", "checkbox": {"equals": True}}

    def test_serialize_does_not_equal(self) -> None:
        f = CheckboxFilter(
            property="Done", checkbox=CheckboxCondition(does_not_equal=False)
        )
        result = f.model_dump(mode="json")
        assert result == {"property": "Done", "checkbox": {"does_not_equal": False}}


class TestNumberFilter:
    def test_serialize_greater_than(self) -> None:
        f = NumberFilter(property="Price", number=NumberCondition(greater_than=100))
        result = f.model_dump(mode="json")
        assert result == {"property": "Price", "number": {"greater_than": 100}}

    def test_serialize_is_empty(self) -> None:
        f = NumberFilter(property="Price", number=NumberCondition(is_empty=True))
        result = f.model_dump(mode="json")
        assert result == {"property": "Price", "number": {"is_empty": True}}


class TestRichTextFilter:
    def test_serialize_contains(self) -> None:
        f = RichTextFilter(property="Name", rich_text=TextCondition(contains="hello"))
        result = f.model_dump(mode="json")
        assert result == {"property": "Name", "rich_text": {"contains": "hello"}}

    def test_serialize_starts_with(self) -> None:
        f = RichTextFilter(property="Title", rich_text=TextCondition(starts_with="A"))
        result = f.model_dump(mode="json")
        assert result == {"property": "Title", "rich_text": {"starts_with": "A"}}


class TestSelectFilter:
    def test_serialize_equals_string(self) -> None:
        f = SelectFilter(property="Status", select=SelectCondition(equals="Active"))
        result = f.model_dump(mode="json")
        assert result == {"property": "Status", "select": {"equals": "Active"}}

    def test_serialize_equals_list(self) -> None:
        f = SelectFilter(
            property="Status", select=SelectCondition(equals=["Active", "Pending"])
        )
        result = f.model_dump(mode="json")
        assert result == {
            "property": "Status",
            "select": {"equals": ["Active", "Pending"]},
        }


class TestMultiSelectFilter:
    def test_serialize_contains(self) -> None:
        f = MultiSelectFilter(
            property="Tags", multi_select=MultiSelectCondition(contains="python")
        )
        result = f.model_dump(mode="json")
        assert result == {"property": "Tags", "multi_select": {"contains": "python"}}


class TestStatusFilter:
    def test_serialize_equals(self) -> None:
        f = StatusFilter(property="Stage", status=StatusCondition(equals="In Progress"))
        result = f.model_dump(mode="json")
        assert result == {"property": "Stage", "status": {"equals": "In Progress"}}


class TestDateFilter:
    def test_serialize_after(self) -> None:
        f = DateFilter(property="Due", date=DateCondition(after="2025-01-01"))
        result = f.model_dump(mode="json")
        assert result == {"property": "Due", "date": {"after": "2025-01-01"}}

    def test_serialize_this_week(self) -> None:
        f = DateFilter(property="Due", date=DateCondition(this_week={}))
        result = f.model_dump(mode="json")
        assert result == {"property": "Due", "date": {"this_week": {}}}


class TestPeopleFilter:
    def test_serialize_contains_user_id(self) -> None:
        uid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        f = PeopleFilter(property="Assignee", people=PeopleCondition(contains=uid))
        result = f.model_dump(mode="json")
        assert result == {"property": "Assignee", "people": {"contains": uid}}


class TestFilesFilter:
    def test_serialize_is_not_empty(self) -> None:
        f = FilesFilter(property="Attachments", files=FilesCondition(is_not_empty=True))
        result = f.model_dump(mode="json")
        assert result == {
            "property": "Attachments",
            "files": {"is_not_empty": True},
        }


class TestUniqueIdFilter:
    def test_serialize_equals(self) -> None:
        f = UniqueIdFilter(property="ID", unique_id=NumberCondition(equals=42))
        result = f.model_dump(mode="json")
        assert result == {"property": "ID", "unique_id": {"equals": 42}}


class TestVerificationFilter:
    def test_serialize_verified(self) -> None:
        f = VerificationFilter(
            property="Verification",
            verification=VerificationCondition(status=VerificationStatus.VERIFIED),
        )
        result = f.model_dump(mode="json")
        assert result == {
            "property": "Verification",
            "verification": {"status": "verified"},
        }


class TestTimestampFilter:
    def test_serialize_created_time_after(self) -> None:
        f = TimestampFilter(
            timestamp=TimestampType.CREATED_TIME,
            condition=DateCondition(after="2025-01-01"),
        )
        result = f.model_dump(mode="json")
        assert result == {
            "timestamp": "created_time",
            "created_time": {"after": "2025-01-01"},
        }

    def test_serialize_last_edited_time_before(self) -> None:
        f = TimestampFilter(
            timestamp=TimestampType.LAST_EDITED_TIME,
            condition=DateCondition(before="2025-06-01"),
        )
        result = f.model_dump(mode="json")
        assert result == {
            "timestamp": "last_edited_time",
            "last_edited_time": {"before": "2025-06-01"},
        }


class TestCompoundFilter:
    def test_serialize_and(self) -> None:
        f = CompoundFilter(
            and_=[
                CheckboxFilter(
                    property="Done", checkbox=CheckboxCondition(equals=True)
                ),
                NumberFilter(property="Price", number=NumberCondition(greater_than=50)),
            ]
        )
        result = f.model_dump(mode="json", by_alias=True)
        assert result == {
            "and": [
                {"property": "Done", "checkbox": {"equals": True}},
                {"property": "Price", "number": {"greater_than": 50}},
            ]
        }

    def test_serialize_or(self) -> None:
        f = CompoundFilter(
            or_=[
                SelectFilter(
                    property="Status", select=SelectCondition(equals="Active")
                ),
                SelectFilter(
                    property="Status", select=SelectCondition(equals="Pending")
                ),
            ]
        )
        result = f.model_dump(mode="json", by_alias=True)
        assert result == {
            "or": [
                {"property": "Status", "select": {"equals": "Active"}},
                {"property": "Status", "select": {"equals": "Pending"}},
            ]
        }

    def test_serialize_nested_compound(self) -> None:
        inner = CompoundFilter(
            or_=[
                NumberFilter(property="A", number=NumberCondition(equals=1)),
                NumberFilter(property="B", number=NumberCondition(equals=2)),
            ]
        )
        outer = CompoundFilter(
            and_=[
                CheckboxFilter(
                    property="Active", checkbox=CheckboxCondition(equals=True)
                ),
                inner,
            ]
        )
        result = outer.model_dump(mode="json", by_alias=True)
        assert result["and"][0] == {
            "property": "Active",
            "checkbox": {"equals": True},
        }
        assert result["and"][1] == {
            "or": [
                {"property": "A", "number": {"equals": 1}},
                {"property": "B", "number": {"equals": 2}},
            ]
        }


class TestPropertySort:
    def test_serialize_ascending(self) -> None:
        s = PropertySort(property="Name", direction=SortDirection.ASCENDING)
        result = s.model_dump(mode="json")
        assert result == {"property": "Name", "direction": "ascending"}

    def test_serialize_descending(self) -> None:
        s = PropertySort(property="Price", direction=SortDirection.DESCENDING)
        result = s.model_dump(mode="json")
        assert result == {"property": "Price", "direction": "descending"}

    def test_default_direction_is_ascending(self) -> None:
        s = PropertySort(property="Name")
        assert s.direction == SortDirection.ASCENDING


class TestTimestampSort:
    def test_serialize_created_time(self) -> None:
        s = TimestampSort(timestamp="created_time", direction=SortDirection.DESCENDING)
        result = s.model_dump(mode="json")
        assert result == {"timestamp": "created_time", "direction": "descending"}


class TestQueryDataSourceRequest:
    def test_to_api_payload_empty(self) -> None:
        req = QueryDataSourceRequest()
        assert req.to_api_payload() == {}

    def test_to_api_payload_with_filter(self) -> None:
        req = QueryDataSourceRequest(
            filter=CheckboxFilter(
                property="Done", checkbox=CheckboxCondition(equals=True)
            )
        )
        payload = req.to_api_payload()
        assert payload["filter"] == {"property": "Done", "checkbox": {"equals": True}}

    def test_to_api_payload_with_sorts(self) -> None:
        req = QueryDataSourceRequest(
            sorts=[PropertySort(property="Name", direction=SortDirection.ASCENDING)]
        )
        payload = req.to_api_payload()
        assert payload["sorts"] == [{"property": "Name", "direction": "ascending"}]

    def test_to_api_payload_with_page_size(self) -> None:
        req = QueryDataSourceRequest(page_size=50)
        payload = req.to_api_payload()
        assert payload["page_size"] == 50

    def test_to_api_payload_with_in_trash(self) -> None:
        req = QueryDataSourceRequest(in_trash=True)
        payload = req.to_api_payload()
        assert payload["in_trash"] is True

    def test_to_query_params_with_filter_properties(self) -> None:
        req = QueryDataSourceRequest(filter_properties=["Name", "Status"])
        params = req.to_query_params()
        assert params == {"filter_properties": ["Name", "Status"]}

    def test_to_query_params_empty(self) -> None:
        req = QueryDataSourceRequest()
        assert req.to_query_params() == {}

    def test_default_result_type_is_page(self) -> None:
        req = QueryDataSourceRequest()
        assert req.result_type == QueryResultType.PAGE

    def test_invalid_page_size_too_large(self) -> None:
        with pytest.raises(ValidationError, match="less than or equal to 100"):
            QueryDataSourceRequest(page_size=200)

    def test_invalid_page_size_zero(self) -> None:
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            QueryDataSourceRequest(page_size=0)
