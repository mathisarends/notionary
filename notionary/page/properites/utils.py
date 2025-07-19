from typing import Any


def extract_property_value(prop_data: dict) -> Any:
    """
    Extract the value of a Notion property from its data dict.
    Supports all common Notion property types.

    Args:
        prop_data: The property data dictionary from Notion API

    Returns:
        The extracted value based on property type
    """
    prop_type = prop_data.get("type")
    if not prop_type:
        return None

    # Handler dictionary for different property types
    handlers = {
        "title": lambda: "".join(
            t.get("plain_text", "") for t in prop_data.get("title", [])
        ),
        "rich_text": lambda: "".join(
            t.get("plain_text", "") for t in prop_data.get("rich_text", [])
        ),
        "number": lambda: prop_data.get("number"),
        "select": lambda: (
            prop_data.get("select", {}).get("name") if prop_data.get("select") else None
        ),
        "multi_select": lambda: [
            o.get("name") for o in prop_data.get("multi_select", [])
        ],
        "status": lambda: (
            prop_data.get("status", {}).get("name") if prop_data.get("status") else None
        ),
        "date": lambda: prop_data.get("date"),
        "checkbox": lambda: prop_data.get("checkbox"),
        "url": lambda: prop_data.get("url"),
        "email": lambda: prop_data.get("email"),
        "phone_number": lambda: prop_data.get("phone_number"),
        "people": lambda: [p.get("id") for p in prop_data.get("people", [])],
        "files": lambda: [
            (
                f.get("external", {}).get("url")
                if f.get("type") == "external"
                else f.get("name")
            )
            for f in prop_data.get("files", [])
        ],
    }

    handler = handlers.get(prop_type)
    if handler is None:
        return prop_data  # Return raw data if type unknown

    try:
        return handler()
    except Exception:
        return None  # Return None if extraction fails
