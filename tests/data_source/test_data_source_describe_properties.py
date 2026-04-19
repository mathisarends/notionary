from unittest.mock import AsyncMock
from uuid import UUID

from notionary.data_source.data_source import DataSource
from notionary.data_source.properties.schemas import (
    DataSourceDateProperty,
    DataSourceMultiSelectConfig,
    DataSourceMultiSelectProperty,
    DataSourceNumberConfig,
    DataSourceNumberProperty,
    DataSourcePropertyOption,
    DataSourceSelectConfig,
    DataSourceSelectProperty,
    DataSourceStatusConfig,
    DataSourceStatusGroup,
    DataSourceStatusProperty,
    DataSourceTitleProperty,
    NumberFormat,
    PropertyColor,
)
from notionary.user.schemas import PartialUserDto

DS_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
OPT_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _option(name: str) -> DataSourcePropertyOption:
    return DataSourcePropertyOption(id=OPT_ID, name=name, color=PropertyColor.DEFAULT)


def _make_data_source(properties: dict) -> DataSource:
    http = AsyncMock()
    return DataSource(
        id=DS_ID,
        url="https://notion.so/ds",
        title="Test DS",
        description=None,
        icon=None,
        cover=None,
        in_trash=False,
        properties=properties,
        http=http,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


class TestDescribeProperties:
    def test_status_property_shows_options_and_groups(self) -> None:
        props = {
            "Status": DataSourceStatusProperty(
                id=OPT_ID,
                name="Status",
                status=DataSourceStatusConfig(
                    options=[_option("Not started"), _option("Done")],
                    groups=[
                        DataSourceStatusGroup(
                            id=OPT_ID,
                            name="To-do",
                            color=PropertyColor.DEFAULT,
                            option_ids=[],
                        )
                    ],
                ),
            )
        }
        result = _make_data_source(props).describe_properties()

        assert result["Status"]["type"] == "status"
        assert result["Status"]["options"] == ["Not started", "Done"]
        assert result["Status"]["groups"] == ["To-do"]

    def test_select_property_shows_options(self) -> None:
        props = {
            "Priority": DataSourceSelectProperty(
                id=OPT_ID,
                name="Priority",
                select=DataSourceSelectConfig(
                    options=[_option("High"), _option("Low")]
                ),
            )
        }
        result = _make_data_source(props).describe_properties()

        assert result["Priority"]["type"] == "select"
        assert result["Priority"]["options"] == ["High", "Low"]

    def test_multi_select_property_shows_options(self) -> None:
        props = {
            "Tags": DataSourceMultiSelectProperty(
                id=OPT_ID,
                name="Tags",
                multi_select=DataSourceMultiSelectConfig(
                    options=[_option("A"), _option("B"), _option("C")]
                ),
            )
        }
        result = _make_data_source(props).describe_properties()

        assert result["Tags"]["type"] == "multi_select"
        assert result["Tags"]["options"] == ["A", "B", "C"]

    def test_number_property_shows_format(self) -> None:
        props = {
            "Price": DataSourceNumberProperty(
                id=OPT_ID,
                name="Price",
                number=DataSourceNumberConfig(format=NumberFormat.EURO),
            )
        }
        result = _make_data_source(props).describe_properties()

        assert result["Price"]["type"] == "number"
        assert result["Price"]["format"] == NumberFormat.EURO

    def test_plain_type_only_for_other_properties(self) -> None:
        props = {
            "Name": DataSourceTitleProperty(id=OPT_ID, name="Name"),
            "Due": DataSourceDateProperty(id=OPT_ID, name="Due"),
        }
        result = _make_data_source(props).describe_properties()

        assert result["Name"] == {"type": "title"}
        assert result["Due"] == {"type": "date"}

    def test_empty_properties(self) -> None:
        result = _make_data_source({}).describe_properties()
        assert result == {}
