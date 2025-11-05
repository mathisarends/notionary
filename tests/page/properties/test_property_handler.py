from unittest.mock import AsyncMock

import pytest

from notionary.exceptions.properties import (
    AccessPagePropertyWithoutDataSourceError,
    PagePropertyNotFoundError,
    PagePropertyTypeError,
)
from notionary.page.properties.schemas import (
    DateValue,
    PageCheckboxProperty,
    PageCreatedTimeProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePhoneNumberProperty,
    PageProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
    SelectOption,
    StatusOption,
)
from notionary.page.properties.service import PagePropertyHandler
from notionary.rich_text.schemas import RichText, TextContent
from notionary.shared.models.parent import ParentType

# ============================================================================
# Property Factory Functions
# ============================================================================


def create_rich_text(text: str) -> RichText:
    return RichText(
        type="text",
        text=TextContent(content=text),
        plain_text=text,
        href=None,
        annotations={},
    )


def create_status_property(
    name: str = "Status",
    status_name: str | None = "In Progress",
    property_id: str = "status_id",
) -> PageStatusProperty:
    status = StatusOption(id="status_opt_id", name=status_name) if status_name else None
    return PageStatusProperty(id=property_id, type="status", status=status)


def create_select_property(
    name: str = "Priority",
    option_name: str | None = "High",
    property_id: str = "select_id",
) -> PageSelectProperty:
    select = SelectOption(id="select_opt_id", name=option_name) if option_name else None
    return PageSelectProperty(id=property_id, type="select", select=select)


def create_title_property(
    title_text: str = "Test Title",
    property_id: str = "title_id",
) -> PageTitleProperty:
    return PageTitleProperty(
        id=property_id,
        type="title",
        title=[create_rich_text(title_text)],
    )


def create_multiselect_property(
    options: list[str] | None = None,
    property_id: str = "multiselect_id",
) -> PageMultiSelectProperty:
    if options is None:
        options = ["Tag1", "Tag2"]

    select_options = [
        SelectOption(id=f"opt_{i}", name=opt) for i, opt in enumerate(options)
    ]
    return PageMultiSelectProperty(
        id=property_id,
        type="multi_select",
        multi_select=select_options,
    )


def create_url_property(
    url: str | None = "https://example.com",
    property_id: str = "url_id",
) -> PageURLProperty:
    return PageURLProperty(id=property_id, type="url", url=url)


def create_number_property(
    number: float | None = 42.5,
    property_id: str = "number_id",
) -> PageNumberProperty:
    return PageNumberProperty(id=property_id, type="number", number=number)


def create_checkbox_property(
    checked: bool = True,
    property_id: str = "checkbox_id",
) -> PageCheckboxProperty:
    return PageCheckboxProperty(id=property_id, type="checkbox", checkbox=checked)


def create_date_property(
    start_date: str | None = "2025-01-15",
    property_id: str = "date_id",
) -> PageDateProperty:
    date_value = DateValue(start=start_date) if start_date else None
    return PageDateProperty(id=property_id, type="date", date=date_value)


def create_rich_text_property(
    text: str = "Rich text content",
    property_id: str = "richtext_id",
) -> PageRichTextProperty:
    return PageRichTextProperty(
        id=property_id,
        type="rich_text",
        rich_text=[create_rich_text(text)],
    )


def create_email_property(
    email: str | None = "test@example.com",
    property_id: str = "email_id",
) -> PageEmailProperty:
    return PageEmailProperty(id=property_id, type="email", email=email)


def create_phone_property(
    phone: str | None = "+1234567890",
    property_id: str = "phone_id",
) -> PagePhoneNumberProperty:
    return PagePhoneNumberProperty(
        id=property_id, type="phone_number", phone_number=phone
    )


def create_created_time_property(
    created_time: str = "2025-01-15T10:00:00.000Z",
    property_id: str = "created_id",
) -> PageCreatedTimeProperty:
    return PageCreatedTimeProperty(
        id=property_id, type="created_time", created_time=created_time
    )


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_http_client() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_properties() -> dict[str, PageProperty]:
    return {
        "Status": create_status_property(),
        "Priority": create_select_property(),
        "Title": create_title_property(),
        "Tags": create_multiselect_property(),
        "URL": create_url_property(),
        "Count": create_number_property(),
        "Done": create_checkbox_property(),
        "Due Date": create_date_property(),
        "Description": create_rich_text_property(),
        "Email": create_email_property(),
        "Phone": create_phone_property(),
        "Created": create_created_time_property(),
    }


@pytest.fixture
def handler(
    sample_properties: dict[str, PageProperty], mock_http_client: AsyncMock
) -> PagePropertyHandler:
    return PagePropertyHandler(
        properties=sample_properties,
        parent_type=ParentType.DATABASE_ID,
        page_url="https://notion.so/test-page",
        page_property_http_client=mock_http_client,
        parent_data_source="test_database_id",
    )


@pytest.fixture
def handler_without_data_source(
    sample_properties: dict[str, PageProperty], mock_http_client: AsyncMock
) -> PagePropertyHandler:
    return PagePropertyHandler(
        properties=sample_properties,
        parent_type=ParentType.PAGE_ID,
        page_url="https://notion.so/test-page",
        page_property_http_client=mock_http_client,
        parent_data_source="",
    )


# ============================================================================
# Tests - Reader Methods
# ============================================================================


def test_get_status_property_value(handler: PagePropertyHandler) -> None:
    status = handler.get_value_of_status_property("Status")
    assert status == "In Progress"


def test_get_status_property_when_none(handler: PagePropertyHandler) -> None:
    handler._properties["Status"] = create_status_property(status_name=None)
    status = handler.get_value_of_status_property("Status")
    assert status is None


def test_get_select_property_value(handler: PagePropertyHandler) -> None:
    priority = handler.get_value_of_select_property("Priority")
    assert priority == "High"


def test_get_select_property_when_none(handler: PagePropertyHandler) -> None:
    handler._properties["Priority"] = create_select_property(option_name=None)
    priority = handler.get_value_of_select_property("Priority")
    assert priority is None


@pytest.mark.asyncio
async def test_get_title_property_value(handler: PagePropertyHandler) -> None:
    handler._rich_text_converter = AsyncMock()
    handler._rich_text_converter.to_markdown = AsyncMock(return_value="Test Title")

    title = await handler.get_value_of_title_property("Title")
    assert title == "Test Title"
    handler._rich_text_converter.to_markdown.assert_called_once()


def test_get_multiselect_property_values(handler: PagePropertyHandler) -> None:
    tags = handler.get_values_of_multiselect_property("Tags")
    assert tags == ["Tag1", "Tag2"]


def test_get_url_property_value(handler: PagePropertyHandler) -> None:
    url = handler.get_value_of_url_property("URL")
    assert url == "https://example.com"


def test_get_number_property_value(handler: PagePropertyHandler) -> None:
    count = handler.get_value_of_number_property("Count")
    assert count == 42.5


def test_get_checkbox_property_value(handler: PagePropertyHandler) -> None:
    done = handler.get_value_of_checkbox_property("Done")
    assert done is True


def test_get_date_property_value(handler: PagePropertyHandler) -> None:
    date = handler.get_value_of_date_property("Due Date")
    assert date == "2025-01-15"


def test_get_date_property_when_none(handler: PagePropertyHandler) -> None:
    handler._properties["Due Date"] = create_date_property(start_date=None)
    date = handler.get_value_of_date_property("Due Date")
    assert date is None


@pytest.mark.asyncio
async def test_get_rich_text_property_value(handler: PagePropertyHandler) -> None:
    handler._rich_text_converter = AsyncMock()
    handler._rich_text_converter.to_markdown = AsyncMock(
        return_value="Rich text content"
    )

    text = await handler.get_value_of_rich_text_property("Description")
    assert text == "Rich text content"
    handler._rich_text_converter.to_markdown.assert_called_once()


def test_get_email_property_value(handler: PagePropertyHandler) -> None:
    email = handler.get_value_of_email_property("Email")
    assert email == "test@example.com"


def test_get_phone_property_value(handler: PagePropertyHandler) -> None:
    phone = handler.get_value_of_phone_number_property("Phone")
    assert phone == "+1234567890"


def test_get_created_time_property_value(handler: PagePropertyHandler) -> None:
    created = handler.get_value_of_created_time_property("Created")
    assert created == "2025-01-15T10:00:00.000Z"


def test_empty_multiselect_returns_empty_list(handler: PagePropertyHandler) -> None:
    handler._properties["Tags"] = create_multiselect_property(options=[])
    tags = handler.get_values_of_multiselect_property("Tags")
    assert tags == []


# ============================================================================
# Tests - Error Handling
# ============================================================================


def test_property_not_found_raises_error(handler: PagePropertyHandler) -> None:
    with pytest.raises(PagePropertyNotFoundError) as exc_info:
        handler.get_value_of_status_property("NonExistent")

    assert "NonExistent" in str(exc_info.value)


def test_wrong_property_type_raises_error(handler: PagePropertyHandler) -> None:
    with pytest.raises(PagePropertyTypeError) as exc_info:
        handler.get_value_of_select_property("Status")

    assert "Status" in str(exc_info.value)


# ============================================================================
# Tests - Data Source Methods
# ============================================================================


@pytest.mark.asyncio
async def test_get_options_without_data_source_raises_error(
    handler_without_data_source: PagePropertyHandler,
) -> None:
    with pytest.raises(AccessPagePropertyWithoutDataSourceError):
        await handler_without_data_source.get_select_options_by_property_name(
            "Priority"
        )
