from typing import Any, Dict, Optional

from notionary.util.logging_mixin import LoggingMixin

class NotionPropertyFormatter(LoggingMixin):
    """Klasse zur Formatierung von Notion-Eigenschaften nach Typ."""
    
    def __init__(self):
        # Mapping von Typen zu Formatierungsmethoden
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
            "relation": self.format_relation
        }
    
    def format_title(self, value: Any) -> Dict[str, Any]:
        """Formatiert einen Titel-Wert."""
        return {
            "title": [
                {
                    "type": "text",
                    "text": {"content": str(value)}
                }
            ]
        }
    
    def format_rich_text(self, value: Any) -> Dict[str, Any]:
        """Formatiert einen Rich-Text-Wert."""
        return {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": str(value)}
                }
            ]
        }
    
    def format_url(self, value: str) -> Dict[str, Any]:
        """Formatiert eine URL."""
        return {"url": value}
    
    def format_email(self, value: str) -> Dict[str, Any]:
        """Formatiert eine E-Mail-Adresse."""
        return {"email": value}
    
    def format_phone_number(self, value: str) -> Dict[str, Any]:
        """Formatiert eine Telefonnummer."""
        return {"phone_number": value}
    
    def format_number(self, value: Any) -> Dict[str, Any]:
        """Formatiert eine Zahl."""
        return {"number": float(value)}
    
    def format_checkbox(self, value: Any) -> Dict[str, Any]:
        """Formatiert einen Checkbox-Wert."""
        return {"checkbox": bool(value)}
    
    def format_select(self, value: str) -> Dict[str, Any]:
        """Formatiert einen Select-Wert."""
        return {"select": {"name": str(value)}}
    
    def format_multi_select(self, value: Any) -> Dict[str, Any]:
        """Formatiert einen Multi-Select-Wert."""
        if isinstance(value, list):
            return {"multi_select": [{"name": item} for item in value]}
        return {"multi_select": [{"name": str(value)}]}
    
    def format_date(self, value: Any) -> Dict[str, Any]:
        """Formatiert ein Datum."""
        if isinstance(value, dict) and "start" in value:
            return {"date": value}
        return {"date": {"start": str(value)}}
    
    def format_status(self, value: str) -> Dict[str, Any]:
        """Formatiert einen Status-Wert."""
        return {"status": {"name": str(value)}}
    
    def format_relation(self, value: Any) -> Dict[str, Any]:
        """Formatiert einen Relations-Wert."""
        if isinstance(value, list):
            return {"relation": [{"id": item} for item in value]}
        return {"relation": [{"id": str(value)}]}
    
    def format_value(self, property_type: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Formatiert einen Wert entsprechend des angegebenen Eigenschaftstyps.
        
        Args:
            property_type: Notion-Eigenschaftstyp (z.B. "title", "rich_text", "status")
            value: Der zu formatierende Wert
            
        Returns:
            Formatierter Wert als Dictionary oder None bei unbekanntem Typ
        """
        formatter = self._formatters.get(property_type)
        if not formatter:
            if self.logger:
                self.logger.warning("Unbekannter Eigenschaftstyp: %s", property_type)
            return None
        
        return formatter(value)