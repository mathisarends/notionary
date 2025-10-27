import pytest

from notionary.data_source.properties.schemas import (
    DataSourceCheckboxProperty,
    DataSourceDateProperty,
    DataSourceEmailProperty,
    DataSourceMultiSelectProperty,
    DataSourceNumberProperty,
    DataSourcePhoneNumberProperty,
    DataSourceProperty,
    DataSourceRichTextProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
    DataSourceTitleProperty,
    DataSourceURLProperty,
)
from notionary.data_source.query.builder import DataSourceQueryBuilder
from notionary.exceptions.data_source.builder import InvalidOperatorForPropertyType
from notionary.shared.properties.type import PropertyType


@pytest.fixture
def properties_for_validation() -> dict[str, DataSourceProperty]:
    return {
        "Title": DataSourceTitleProperty(
            id="title",
            name="Title",
            type=PropertyType.TITLE,
        ),
        "Description": DataSourceRichTextProperty(
            id="description",
            name="Description",
            type=PropertyType.RICH_TEXT,
        ),
        "Status": DataSourceStatusProperty(
            id="status",
            name="Status",
            type=PropertyType.STATUS,
        ),
        "Priority": DataSourceSelectProperty(
            id="priority",
            name="Priority",
            type=PropertyType.SELECT,
        ),
        "Tags": DataSourceMultiSelectProperty(
            id="tags",
            name="Tags",
            type=PropertyType.MULTI_SELECT,
        ),
        "Count": DataSourceNumberProperty(
            id="count",
            name="Count",
            type=PropertyType.NUMBER,
            number={"format": "number"},
        ),
        "Completed": DataSourceCheckboxProperty(
            id="completed",
            name="Completed",
            type=PropertyType.CHECKBOX,
        ),
        "URL": DataSourceURLProperty(
            id="url",
            name="URL",
            type=PropertyType.URL,
        ),
        "Email": DataSourceEmailProperty(
            id="email",
            name="Email",
            type=PropertyType.EMAIL,
        ),
        "Phone": DataSourcePhoneNumberProperty(
            id="phone",
            name="Phone",
            type=PropertyType.PHONE_NUMBER,
        ),
        "Due Date": DataSourceDateProperty(
            id="due_date",
            name="Due Date",
            type=PropertyType.DATE,
        ),
    }


@pytest.fixture
def builder(
    properties_for_validation: dict[str, DataSourceProperty],
) -> DataSourceQueryBuilder:
    return DataSourceQueryBuilder(properties=properties_for_validation)


def test_string_operator_on_status_property_succeeds(
    builder: DataSourceQueryBuilder,
) -> None:
    result = builder.where("Status").equals("Active").build()
    assert result.filter is not None


def test_string_operator_on_select_property_succeeds(
    builder: DataSourceQueryBuilder,
) -> None:
    """SELECT properties support equals (via StatusOperator), not contains"""
    result = builder.where("Priority").equals("High").build()
    assert result.filter is not None


def test_select_does_not_support_contains(builder: DataSourceQueryBuilder) -> None:
    """SELECT properties in Notion API only support equals/does_not_equal, not contains/starts_with/ends_with"""
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Priority").contains("High")

    assert exc_info.value.property_name == "Priority"
    assert "contains" in str(exc_info.value).lower()


def test_select_does_not_support_starts_with(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Priority").starts_with("Hi")

    assert exc_info.value.property_name == "Priority"


def test_select_does_not_support_ends_with(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Priority").ends_with("gh")

    assert exc_info.value.property_name == "Priority"


def test_array_operator_on_multi_select_succeeds(
    builder: DataSourceQueryBuilder,
) -> None:
    result = builder.where("Tags").array_contains("urgent").build()
    assert result.filter is not None


def test_number_operator_on_number_property_succeeds(
    builder: DataSourceQueryBuilder,
) -> None:
    result = builder.where("Count").greater_than(10).build()
    assert result.filter is not None


def test_boolean_operator_on_checkbox_succeeds(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Completed").is_true().build()
    assert result.filter is not None


def test_array_operator_on_status_property_raises_error(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Status").array_contains("Active")

    assert exc_info.value.property_name == "Status"
    assert exc_info.value.property_type == PropertyType.STATUS
    assert "contains" in str(exc_info.value).lower()


def test_number_operator_on_status_property_raises_error(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Status").greater_than(5)

    assert exc_info.value.property_name == "Status"
    assert "greater_than" in str(exc_info.value).lower()


def test_boolean_operator_on_select_property_raises_error(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Priority").is_true()

    assert exc_info.value.property_name == "Priority"
    assert "is_true" in str(exc_info.value).lower()


def test_string_operator_on_checkbox_property_raises_error(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Completed").contains("true")

    assert exc_info.value.property_name == "Completed"
    assert "contains" in str(exc_info.value).lower()


def test_string_operator_on_multi_select_raises_error(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Tags").equals("urgent")

    assert exc_info.value.property_name == "Tags"
    assert "equals" in str(exc_info.value).lower()


def test_number_operator_on_multi_select_raises_error(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Tags").less_than(5)

    assert exc_info.value.property_name == "Tags"
    assert "less_than" in str(exc_info.value).lower()


def test_error_message_includes_valid_operators(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Status").array_contains("Active")

    error_message = str(exc_info.value)
    assert "valid operators" in error_message.lower()
    assert "equals" in error_message.lower()
    assert "contains" in error_message.lower()


def test_error_message_shows_property_type(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Priority").greater_than(10)

    error_message = str(exc_info.value)
    assert "select" in error_message.lower()


def test_validation_works_with_where_not(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(InvalidOperatorForPropertyType):
        builder.where_not("Status").greater_than(5)


def test_validation_works_with_and_where(builder: DataSourceQueryBuilder) -> None:
    builder.where("Status").equals("Active")

    with pytest.raises(InvalidOperatorForPropertyType):
        builder.and_where("Priority").is_true()


def test_validation_works_with_or_where(builder: DataSourceQueryBuilder) -> None:
    builder.where("Status").equals("Active")

    with pytest.raises(InvalidOperatorForPropertyType):
        builder.or_where("Tags").equals("urgent")


def test_multiple_valid_operators_on_same_property(
    builder: DataSourceQueryBuilder,
) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .and_where("Status")
        .does_not_equal("Inactive")
        .and_where("Status")
        .is_not_empty()
        .build()
    )
    assert result.filter is not None


def test_validation_with_negation(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(InvalidOperatorForPropertyType):
        builder.where_not("Completed").contains("text")


# ============================================================================
# Text Properties - Support full string operations
# ============================================================================


def test_title_supports_contains(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Title").contains("Project").build()
    assert result.filter is not None


def test_title_supports_starts_with(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Title").starts_with("Project").build()
    assert result.filter is not None


def test_title_supports_ends_with(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Title").ends_with("2024").build()
    assert result.filter is not None


def test_rich_text_supports_contains(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Description").contains("urgent").build()
    assert result.filter is not None


def test_url_supports_contains(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("URL").contains("github.com").build()
    assert result.filter is not None


def test_email_supports_contains(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Email").contains("@example.com").build()
    assert result.filter is not None


def test_phone_supports_starts_with(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Phone").starts_with("+49").build()
    assert result.filter is not None


# ============================================================================
# Date Properties
# ============================================================================


def test_date_supports_before(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").before("2024-12-31").build()
    assert result.filter is not None


def test_date_does_not_support_contains(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(InvalidOperatorForPropertyType) as exc_info:
        builder.where("Due Date").contains("2024")

    assert exc_info.value.property_name == "Due Date"
    assert "contains" in str(exc_info.value).lower()
