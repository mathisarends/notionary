from unittest.mock import AsyncMock, Mock
from uuid import UUID

from notionary.data_source.data_source import DataSource
from notionary.data_source.properties.schemas import (
    DataSourceDateProperty,
    DataSourceMultiSelectConfig,
    DataSourceMultiSelectProperty,
    DataSourceNumberConfig,
    DataSourceNumberProperty,
    DataSourcePropertyOption,
    DataSourceRelationConfig,
    DataSourceRelationProperty,
    DataSourceSelectConfig,
    DataSourceSelectProperty,
    DataSourceStatusConfig,
    DataSourceStatusGroup,
    DataSourceStatusProperty,
    DataSourceTitleProperty,
    DataSourceUnknownProperty,
    NumberFormat,
    PropertyColor,
)
from notionary.data_source.properties.views import (
    DataSourcePropertyDescription,
    DataSourceRelationOption,
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

        assert result["Status"].type == "status"
        assert result["Status"].options == ["Not started", "Done"]
        assert result["Status"].groups == ["To-do"]

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

        assert result["Priority"].type == "select"
        assert result["Priority"].options == ["High", "Low"]

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

        assert result["Tags"].type == "multi_select"
        assert result["Tags"].options == ["A", "B", "C"]

    def test_relation_property_shows_relation_option_with_id_and_title(self) -> None:
        related_data_source_id = UUID("11111111-1111-1111-1111-111111111111")
        props = {
            "Module": DataSourceRelationProperty(
                id=OPT_ID,
                name="Module",
                relation=DataSourceRelationConfig(
                    data_source_id=related_data_source_id
                ),
            )
        }
        result = _make_data_source(props).describe_properties()

        assert result["Module"].type == "relation"
        assert result["Module"].relation_options == [
            DataSourceRelationOption(
                id=str(related_data_source_id),
                title="Module",
            )
        ]

    def test_number_property_shows_format(self) -> None:
        props = {
            "Price": DataSourceNumberProperty(
                id=OPT_ID,
                name="Price",
                number=DataSourceNumberConfig(format=NumberFormat.EURO),
            )
        }
        result = _make_data_source(props).describe_properties()

        assert result["Price"].type == "number"
        assert result["Price"].format == NumberFormat.EURO

    def test_plain_type_only_for_other_properties(self) -> None:
        props = {
            "Name": DataSourceTitleProperty(id=OPT_ID, name="Name"),
            "Due": DataSourceDateProperty(id=OPT_ID, name="Due"),
        }
        result = _make_data_source(props).describe_properties()

        assert result["Name"] == DataSourcePropertyDescription(type="title")
        assert result["Due"] == DataSourcePropertyDescription(type="date")

    def test_empty_properties(self) -> None:
        result = _make_data_source({}).describe_properties()
        assert result == {}

    def test_describe_properties_delegates_to_properties_service(self) -> None:
        data_source = _make_data_source({})
        expected = {"Status": DataSourcePropertyDescription(type="status")}
        data_source._properties.describe = Mock(return_value=expected)

        result = data_source.describe_properties()

        data_source._properties.describe.assert_called_once_with()
        assert result == expected

    def test_unknown_status_property_extracts_options_and_groups(self) -> None:
        props = {
            "Status": DataSourceUnknownProperty.model_validate(
                {
                    "id": "status-id",
                    "type": "status",
                    "status": {
                        "options": [
                            {"id": "1", "name": "Nicht begonnen", "color": "gray"},
                            {"id": "2", "name": "Pausiert", "color": "blue"},
                            {"id": "3", "name": "In Bearbeitung", "color": "blue"},
                            {"id": "4", "name": "Erledigt", "color": "green"},
                        ],
                        "groups": [
                            {"id": "g1", "name": "To-Do", "color": "gray"},
                            {"id": "g2", "name": "In Bearbeitung", "color": "blue"},
                            {"id": "g3", "name": "Abgeschlossen", "color": "green"},
                        ],
                    },
                }
            )
        }

        result = _make_data_source(props).describe_properties()

        assert result["Status"].type == "status"
        assert result["Status"].options == [
            "Nicht begonnen",
            "Pausiert",
            "In Bearbeitung",
            "Erledigt",
        ]
        assert result["Status"].groups == [
            "To-Do",
            "In Bearbeitung",
            "Abgeschlossen",
        ]

    def test_unknown_select_property_extracts_options(self) -> None:
        props = {
            "Priorität": DataSourceUnknownProperty.model_validate(
                {
                    "id": "priority-id",
                    "type": "select",
                    "select": {
                        "options": [
                            {"id": "p1", "name": "Hoch", "color": "green"},
                            {"id": "p2", "name": "Mittel", "color": "pink"},
                            {"id": "p3", "name": "Niedrig", "color": "brown"},
                        ]
                    },
                }
            )
        }

        result = _make_data_source(props).describe_properties()

        assert result["Priorität"].type == "select"
        assert result["Priorität"].options == ["Hoch", "Mittel", "Niedrig"]

    def test_unknown_relation_property_extracts_relation_option(self) -> None:
        props = {
            "Module": DataSourceUnknownProperty.model_validate(
                {
                    "id": "module-id",
                    "type": "relation",
                    "relation": {
                        "data_source_id": "291389d57bd3800f90faf2ef07f120e4",
                        "data_source_name": "Module",
                    },
                }
            )
        }

        result = _make_data_source(props).describe_properties()

        assert result["Module"].type == "relation"
        assert result["Module"].relation_options == [
            DataSourceRelationOption(
                id="291389d57bd3800f90faf2ef07f120e4",
                title="Module",
            )
        ]
