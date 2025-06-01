from typing import Any, Dict, Optional

from notionary.util import LoggingMixin


class NotionPropertyFormatter(LoggingMixin):
    """Class for formatting Notion properties based on their type."""

    def __init__(self):
        self._formatters = {
            "title": self.format_title,
            "rich_text": self.format_rich_text,
            "url": self.format_url,
            "email": self.format_email,
            "phone_number": self.format_phone_number,
            "number": self.format_number,
            "checkbox": self.format_checkbox,
            "select": self.format_select,
            "multi_select": self.format_multi_select,
            "date": self.format_date,
            "status": self.format_status,
            "relation": self.format_relation,
        }

    def format_title(self, value: Any) -> Dict[str, Any]:
        """Formats a title value."""
        return {"title": [{"type": "text", "text": {"content": str(value)}}]}

    def format_rich_text(self, value: Any) -> Dict[str, Any]:
        """Formats a rich text value."""
        return {"rich_text": [{"type": "text", "text": {"content": str(value)}}]}

    def format_url(self, value: str) -> Dict[str, Any]:
        """Formats a URL value."""
        return {"url": value}

    def format_email(self, value: str) -> Dict[str, Any]:
        """Formats an email address."""
        return {"email": value}

    def format_phone_number(self, value: str) -> Dict[str, Any]:
        """Formats a phone number."""
        return {"phone_number": value}

    def format_number(self, value: Any) -> Dict[str, Any]:
        """Formats a numeric value."""
        return {"number": float(value)}

    def format_checkbox(self, value: Any) -> Dict[str, Any]:
        """Formats a checkbox value."""
        return {"checkbox": bool(value)}

    def format_select(self, value: str) -> Dict[str, Any]:
        """Formats a select value."""
        return {"select": {"name": str(value)}}

    def format_multi_select(self, value: Any) -> Dict[str, Any]:
        """Formats a multi-select value."""
        if isinstance(value, list):
            return {"multi_select": [{"name": item} for item in value]}
        return {"multi_select": [{"name": str(value)}]}

    def format_date(self, value: Any) -> Dict[str, Any]:
        """Formats a date value."""
        if isinstance(value, dict) and "start" in value:
            return {"date": value}
        return {"date": {"start": str(value)}}

    def format_status(self, value: str) -> Dict[str, Any]:
        """Formats a status value."""
        return {"status": {"name": str(value)}}

    def format_relation(self, value: Any) -> Dict[str, Any]:
        """Formats a relation value."""
        if isinstance(value, list):
            return {"relation": [{"id": item} for item in value]}
        return {"relation": [{"id": str(value)}]}

    def format_value(self, property_type: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Formats a value according to the given Notion property type.

        Args:
            property_type: Notion property type (e.g., "title", "rich_text", "status")
            value: The value to be formatted

        Returns:
            A dictionary with the formatted value, or None if the type is unknown.
        """
        formatter = self._formatters.get(property_type)
        if not formatter:
            if self.logger:
                self.logger.warning("Unknown property type: %s", property_type)
            return None

        return formatter(value)
