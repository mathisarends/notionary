from notionary.data_source.query.filter_builder import Filter
from notionary.data_source.query.filters import (
    CheckboxCondition,
    CheckboxFilter,
    CompoundFilter,
    DateCondition,
    DateFilter,
    MultiSelectCondition,
    MultiSelectFilter,
    NumberCondition,
    NumberFilter,
    RelationCondition,
    RelationFilter,
    RichTextFilter,
    SelectCondition,
    SelectFilter,
    StatusFilter,
    TextCondition,
    TimestampFilter,
    TimestampType,
)


class TestFilterText:
    def test_contains(self) -> None:
        f = Filter.text("Name").contains("foo")
        assert isinstance(f, RichTextFilter)
        assert f.model_dump(mode="json") == {
            "property": "Name",
            "rich_text": {"contains": "foo"},
        }

    def test_equals(self) -> None:
        f = Filter.text("Title").equals("hello")
        assert f.model_dump(mode="json") == {
            "property": "Title",
            "rich_text": {"equals": "hello"},
        }

    def test_does_not_equal(self) -> None:
        f = Filter.text("Title").does_not_equal("legacy")
        assert f.model_dump(mode="json") == {
            "property": "Title",
            "rich_text": {"does_not_equal": "legacy"},
        }

    def test_starts_with(self) -> None:
        f = Filter.text("Name").starts_with("A")
        assert f.model_dump(mode="json") == {
            "property": "Name",
            "rich_text": {"starts_with": "A"},
        }

    def test_ends_with(self) -> None:
        f = Filter.text("Name").ends_with("z")
        assert f.model_dump(mode="json") == {
            "property": "Name",
            "rich_text": {"ends_with": "z"},
        }

    def test_does_not_contain(self) -> None:
        f = Filter.text("Name").does_not_contain("bad")
        assert f.model_dump(mode="json") == {
            "property": "Name",
            "rich_text": {"does_not_contain": "bad"},
        }

    def test_is_empty(self) -> None:
        f = Filter.text("Name").is_empty()
        assert f.model_dump(mode="json") == {
            "property": "Name",
            "rich_text": {"is_empty": True},
        }

    def test_is_not_empty(self) -> None:
        f = Filter.text("Name").is_not_empty()
        assert f.model_dump(mode="json") == {
            "property": "Name",
            "rich_text": {"is_not_empty": True},
        }


class TestFilterNumber:
    def test_equals(self) -> None:
        f = Filter.number("Price").equals(42)
        assert isinstance(f, NumberFilter)
        assert f.model_dump(mode="json") == {
            "property": "Price",
            "number": {"equals": 42},
        }

    def test_greater_than(self) -> None:
        f = Filter.number("Score").greater_than(90)
        assert f.model_dump(mode="json") == {
            "property": "Score",
            "number": {"greater_than": 90},
        }

    def test_does_not_equal(self) -> None:
        f = Filter.number("Score").does_not_equal(0)
        assert f.model_dump(mode="json") == {
            "property": "Score",
            "number": {"does_not_equal": 0},
        }

    def test_less_than(self) -> None:
        f = Filter.number("Age").less_than(30)
        assert f.model_dump(mode="json") == {
            "property": "Age",
            "number": {"less_than": 30},
        }

    def test_greater_than_or_equal_to(self) -> None:
        f = Filter.number("Age").greater_than_or_equal_to(18)
        assert f.model_dump(mode="json") == {
            "property": "Age",
            "number": {"greater_than_or_equal_to": 18},
        }

    def test_less_than_or_equal_to(self) -> None:
        f = Filter.number("Age").less_than_or_equal_to(65)
        assert f.model_dump(mode="json") == {
            "property": "Age",
            "number": {"less_than_or_equal_to": 65},
        }

    def test_between_produces_compound_and(self) -> None:
        f = Filter.number("Price").between(10, 50)
        assert isinstance(f, CompoundFilter)
        dumped = f.model_dump(mode="json", by_alias=True)
        assert len(dumped["and"]) == 2
        assert dumped["and"][0]["number"]["greater_than_or_equal_to"] == 10
        assert dumped["and"][1]["number"]["less_than_or_equal_to"] == 50

    def test_is_empty(self) -> None:
        f = Filter.number("X").is_empty()
        assert f.model_dump(mode="json") == {
            "property": "X",
            "number": {"is_empty": True},
        }

    def test_is_not_empty(self) -> None:
        f = Filter.number("X").is_not_empty()
        assert f.model_dump(mode="json") == {
            "property": "X",
            "number": {"is_not_empty": True},
        }


class TestFilterSelect:
    def test_equals(self) -> None:
        f = Filter.select("Status").equals("Active")
        assert isinstance(f, SelectFilter)
        assert f.model_dump(mode="json") == {
            "property": "Status",
            "select": {"equals": "Active"},
        }

    def test_not_equals(self) -> None:
        f = Filter.select("Status").not_equals("Done")
        assert f.model_dump(mode="json") == {
            "property": "Status",
            "select": {"does_not_equal": "Done"},
        }

    def test_is_empty(self) -> None:
        f = Filter.select("Priority").is_empty()
        assert f.model_dump(mode="json") == {
            "property": "Priority",
            "select": {"is_empty": True},
        }

    def test_is_not_empty(self) -> None:
        f = Filter.select("Priority").is_not_empty()
        assert f.model_dump(mode="json") == {
            "property": "Priority",
            "select": {"is_not_empty": True},
        }


class TestFilterStatus:
    def test_equals(self) -> None:
        f = Filter.status("Stage").equals("In Progress")
        assert isinstance(f, StatusFilter)
        assert f.model_dump(mode="json") == {
            "property": "Stage",
            "status": {"equals": "In Progress"},
        }

    def test_not_equals(self) -> None:
        f = Filter.status("Stage").not_equals("Done")
        assert f.model_dump(mode="json") == {
            "property": "Stage",
            "status": {"does_not_equal": "Done"},
        }

    def test_is_empty(self) -> None:
        f = Filter.status("Stage").is_empty()
        assert f.model_dump(mode="json") == {
            "property": "Stage",
            "status": {"is_empty": True},
        }

    def test_is_not_empty(self) -> None:
        f = Filter.status("Stage").is_not_empty()
        assert f.model_dump(mode="json") == {
            "property": "Stage",
            "status": {"is_not_empty": True},
        }


class TestFilterCheckbox:
    def test_default_checked_true(self) -> None:
        f = Filter.checkbox("Done")
        assert isinstance(f, CheckboxFilter)
        assert f.model_dump(mode="json") == {
            "property": "Done",
            "checkbox": {"equals": True},
        }

    def test_checked_false(self) -> None:
        f = Filter.checkbox("Done", checked=False)
        assert f.model_dump(mode="json") == {
            "property": "Done",
            "checkbox": {"equals": False},
        }


class TestFilterDate:
    def test_equals(self) -> None:
        f = Filter.date("Due").equals("2025-04-01")
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"equals": "2025-04-01"},
        }

    def test_after(self) -> None:
        f = Filter.date("Due").after("2025-01-01")
        assert isinstance(f, DateFilter)
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"after": "2025-01-01"},
        }

    def test_before(self) -> None:
        f = Filter.date("Due").before("2025-12-31")
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"before": "2025-12-31"},
        }

    def test_on_or_before(self) -> None:
        f = Filter.date("Due").on_or_before("2025-12-31")
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"on_or_before": "2025-12-31"},
        }

    def test_on_or_after(self) -> None:
        f = Filter.date("Due").on_or_after("2025-01-01")
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"on_or_after": "2025-01-01"},
        }

    def test_this_week(self) -> None:
        f = Filter.date("Due").this_week()
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"this_week": {}},
        }

    def test_past_week(self) -> None:
        f = Filter.date("Due").past_week()
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"past_week": {}},
        }

    def test_past_month(self) -> None:
        f = Filter.date("Created").past_month()
        assert f.model_dump(mode="json") == {
            "property": "Created",
            "date": {"past_month": {}},
        }

    def test_past_year(self) -> None:
        f = Filter.date("Created").past_year()
        assert f.model_dump(mode="json") == {
            "property": "Created",
            "date": {"past_year": {}},
        }

    def test_next_week(self) -> None:
        f = Filter.date("Due").next_week()
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"next_week": {}},
        }

    def test_next_month(self) -> None:
        f = Filter.date("Due").next_month()
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"next_month": {}},
        }

    def test_next_year(self) -> None:
        f = Filter.date("Due").next_year()
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"next_year": {}},
        }

    def test_is_empty(self) -> None:
        f = Filter.date("Due").is_empty()
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"is_empty": True},
        }

    def test_is_not_empty(self) -> None:
        f = Filter.date("Due").is_not_empty()
        assert f.model_dump(mode="json") == {
            "property": "Due",
            "date": {"is_not_empty": True},
        }


class TestFilterMultiSelect:
    def test_contains(self) -> None:
        f = Filter.multi_select("Tags").contains("python")
        assert isinstance(f, MultiSelectFilter)
        assert f.model_dump(mode="json") == {
            "property": "Tags",
            "multi_select": {"contains": "python"},
        }

    def test_contains_all_produces_and(self) -> None:
        f = Filter.multi_select("Tags").contains_all("python", "async")
        assert isinstance(f, CompoundFilter)
        dumped = f.model_dump(mode="json", by_alias=True)
        assert len(dumped["and"]) == 2
        assert dumped["and"][0] == {
            "property": "Tags",
            "multi_select": {"contains": "python"},
        }
        assert dumped["and"][1] == {
            "property": "Tags",
            "multi_select": {"contains": "async"},
        }

    def test_contains_any_produces_or(self) -> None:
        f = Filter.multi_select("Tags").contains_any("a", "b")
        dumped = f.model_dump(mode="json", by_alias=True)
        assert len(dumped["or"]) == 2

    def test_does_not_contain(self) -> None:
        f = Filter.multi_select("Tags").does_not_contain("legacy")
        assert f.model_dump(mode="json") == {
            "property": "Tags",
            "multi_select": {"does_not_contain": "legacy"},
        }

    def test_is_empty(self) -> None:
        f = Filter.multi_select("Tags").is_empty()
        assert f.model_dump(mode="json") == {
            "property": "Tags",
            "multi_select": {"is_empty": True},
        }

    def test_is_not_empty(self) -> None:
        f = Filter.multi_select("Tags").is_not_empty()
        assert f.model_dump(mode="json") == {
            "property": "Tags",
            "multi_select": {"is_not_empty": True},
        }


class TestFilterRelation:
    def test_contains(self) -> None:
        uid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        f = Filter.relation("Project").contains(uid)
        assert isinstance(f, RelationFilter)
        assert f.model_dump(mode="json") == {
            "property": "Project",
            "relation": {"contains": uid},
        }

    def test_is_empty(self) -> None:
        f = Filter.relation("Project").is_empty()
        assert f.model_dump(mode="json") == {
            "property": "Project",
            "relation": {"is_empty": True},
        }

    def test_does_not_contain(self) -> None:
        uid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        f = Filter.relation("Project").does_not_contain(uid)
        assert f.model_dump(mode="json") == {
            "property": "Project",
            "relation": {"does_not_contain": uid},
        }

    def test_is_not_empty(self) -> None:
        f = Filter.relation("Project").is_not_empty()
        assert f.model_dump(mode="json") == {
            "property": "Project",
            "relation": {"is_not_empty": True},
        }


class TestFilterCompound:
    def test_all_combines_with_and(self) -> None:
        f = Filter.all(
            Filter.checkbox("Done"),
            Filter.status("Stage").equals("Review"),
        )
        assert isinstance(f, CompoundFilter)
        dumped = f.model_dump(mode="json", by_alias=True)
        assert len(dumped["and"]) == 2

    def test_any_combines_with_or(self) -> None:
        f = Filter.any(
            Filter.select("Priority").equals("High"),
            Filter.select("Priority").equals("Critical"),
        )
        dumped = f.model_dump(mode="json", by_alias=True)
        assert len(dumped["or"]) == 2

    def test_nested_all_and_any(self) -> None:
        f = Filter.all(
            Filter.checkbox("Active"),
            Filter.any(
                Filter.status("Stage").equals("Review"),
                Filter.status("Stage").equals("QA"),
            ),
        )
        dumped = f.model_dump(mode="json", by_alias=True)
        assert len(dumped["and"]) == 2
        assert "or" in dumped["and"][1]


class TestFilterTimestampShortcuts:
    def test_created_this_week(self) -> None:
        f = Filter.created_this_week()
        assert isinstance(f, TimestampFilter)
        assert f.model_dump(mode="json") == {
            "timestamp": "created_time",
            "created_time": {"this_week": {}},
        }

    def test_edited_after(self) -> None:
        f = Filter.edited_after("2025-01-01")
        assert f.model_dump(mode="json") == {
            "timestamp": "last_edited_time",
            "last_edited_time": {"after": "2025-01-01"},
        }

    def test_created_after(self) -> None:
        f = Filter.created_after("2025-06-01")
        assert f.model_dump(mode="json") == {
            "timestamp": "created_time",
            "created_time": {"after": "2025-06-01"},
        }

    def test_created_before(self) -> None:
        f = Filter.created_before("2025-06-01")
        assert f.model_dump(mode="json") == {
            "timestamp": "created_time",
            "created_time": {"before": "2025-06-01"},
        }

    def test_edited_before(self) -> None:
        f = Filter.edited_before("2025-12-31")
        assert f.model_dump(mode="json") == {
            "timestamp": "last_edited_time",
            "last_edited_time": {"before": "2025-12-31"},
        }


class TestFilterBuilderParityWithRawFilters:
    def test_text_builder_matches_raw_filter(self) -> None:
        built = Filter.text("Name").contains("vizro")
        raw = RichTextFilter(
            property="Name",
            rich_text=TextCondition(contains="vizro"),
        )
        assert built.model_dump(mode="json") == raw.model_dump(mode="json")

    def test_number_builder_matches_raw_filter(self) -> None:
        built = Filter.number("Score").greater_than_or_equal_to(7)
        raw = NumberFilter(
            property="Score",
            number=NumberCondition(greater_than_or_equal_to=7),
        )
        assert built.model_dump(mode="json") == raw.model_dump(mode="json")

    def test_select_builder_matches_raw_filter(self) -> None:
        built = Filter.select("Status").not_equals("Done")
        raw = SelectFilter(
            property="Status",
            select=SelectCondition(does_not_equal="Done"),
        )
        assert built.model_dump(mode="json") == raw.model_dump(mode="json")

    def test_date_builder_matches_raw_filter(self) -> None:
        built = Filter.date("Due").on_or_after("2025-05-01")
        raw = DateFilter(
            property="Due",
            date=DateCondition(on_or_after="2025-05-01"),
        )
        assert built.model_dump(mode="json") == raw.model_dump(mode="json")

    def test_multi_select_builder_matches_raw_filter(self) -> None:
        built = Filter.multi_select("Tags").does_not_contain("legacy")
        raw = MultiSelectFilter(
            property="Tags",
            multi_select=MultiSelectCondition(does_not_contain="legacy"),
        )
        assert built.model_dump(mode="json") == raw.model_dump(mode="json")

    def test_relation_builder_matches_raw_filter(self) -> None:
        uid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        built = Filter.relation("Project").contains(uid)
        raw = RelationFilter(
            property="Project",
            relation=RelationCondition(contains=uid),
        )
        assert built.model_dump(mode="json") == raw.model_dump(mode="json")

    def test_checkbox_builder_matches_raw_filter(self) -> None:
        built = Filter.checkbox("Active", checked=False)
        raw = CheckboxFilter(
            property="Active",
            checkbox=CheckboxCondition(equals=False),
        )
        assert built.model_dump(mode="json") == raw.model_dump(mode="json")

    def test_created_after_builder_matches_timestamp_filter(self) -> None:
        built = Filter.created_after("2025-01-01")
        assert built.timestamp == TimestampType.CREATED_TIME
        assert built.model_dump(mode="json") == {
            "timestamp": "created_time",
            "created_time": {"after": "2025-01-01"},
        }
