from dataclasses import dataclass

from notionary.shared.properties.type import PropertyType


@dataclass(frozen=True)
class PropertyTypeDescriptor:
    display_name: str
    description: str


class DatabasePropertyTypeDescriptorRegistry:
    def __init__(self):
        self._DESCRIPTORS = {
            PropertyType.TITLE: PropertyTypeDescriptor(
                display_name="Title", description="Required field for the main heading of the entry"
            ),
            PropertyType.RICH_TEXT: PropertyTypeDescriptor(
                display_name="Rich Text", description="Free-form text field for additional information"
            ),
            PropertyType.NUMBER: PropertyTypeDescriptor(display_name="Number", description="Numeric value field"),
            PropertyType.CHECKBOX: PropertyTypeDescriptor(
                display_name="Checkbox", description="Boolean value (true/false)"
            ),
            PropertyType.DATE: PropertyTypeDescriptor(display_name="Date", description="Date or date range field"),
            PropertyType.URL: PropertyTypeDescriptor(display_name="URL", description="Web address field"),
            PropertyType.EMAIL: PropertyTypeDescriptor(display_name="Email", description="Email address field"),
            PropertyType.PHONE_NUMBER: PropertyTypeDescriptor(
                display_name="Phone Number", description="Phone number field"
            ),
            PropertyType.FILES: PropertyTypeDescriptor(
                display_name="Files & Media", description="Upload or link to files"
            ),
            PropertyType.PEOPLE: PropertyTypeDescriptor(display_name="People", description="Reference to Notion users"),
            PropertyType.SELECT: PropertyTypeDescriptor(
                display_name="Single Select", description="Choose one option from available choices"
            ),
            PropertyType.MULTI_SELECT: PropertyTypeDescriptor(
                display_name="Multi Select", description="Choose multiple options from available choices"
            ),
            PropertyType.STATUS: PropertyTypeDescriptor(
                display_name="Status", description="Track status with predefined options"
            ),
            PropertyType.RELATION: PropertyTypeDescriptor(
                display_name="Relation", description="Link to entries in another database"
            ),
            PropertyType.CREATED_TIME: PropertyTypeDescriptor(
                display_name="Created Time",
                description="Automatically set when the page is created",
            ),
            PropertyType.CREATED_BY: PropertyTypeDescriptor(
                display_name="Created By",
                description="Automatically set to the user who created the page",
            ),
            PropertyType.LAST_EDITED_TIME: PropertyTypeDescriptor(
                display_name="Last Edited Time",
                description="Automatically updated when the page is modified",
            ),
            PropertyType.LAST_EDITED_BY: PropertyTypeDescriptor(
                display_name="Last Edited By",
                description="Automatically set to the user who last edited the page",
            ),
            PropertyType.LAST_VISITED_TIME: PropertyTypeDescriptor(
                display_name="Last Visited Time",
                description="Automatically updated when the page is visited",
            ),
            PropertyType.FORMULA: PropertyTypeDescriptor(
                display_name="Formula",
                description="Computed value based on other properties",
            ),
            PropertyType.ROLLUP: PropertyTypeDescriptor(
                display_name="Rollup",
                description="Aggregate values from related database entries",
            ),
            PropertyType.BUTTON: PropertyTypeDescriptor(
                display_name="Button",
                description="Interactive button that triggers an action",
            ),
            PropertyType.LOCATION: PropertyTypeDescriptor(
                display_name="Location",
                description="Geographic location field",
            ),
            PropertyType.PLACE: PropertyTypeDescriptor(
                display_name="Place",
                description="Place or venue information",
            ),
            PropertyType.VERIFICATION: PropertyTypeDescriptor(
                display_name="Verification",
                description="Verification status field",
            ),
            PropertyType.UNIQUE_ID: PropertyTypeDescriptor(
                display_name="Unique ID",
                description="Auto-generated unique identifier",
            ),
        }

    def get_descriptor(self, property_type: PropertyType) -> PropertyTypeDescriptor:
        return self._DESCRIPTORS.get(
            property_type,
            PropertyTypeDescriptor(display_name=self._format_unknown_type_name(property_type), description=""),
        )

    def _format_unknown_type_name(self, property_type: PropertyType) -> str:
        return property_type.value.replace("_", " ").title()
