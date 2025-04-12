from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PropertyOperationResult:
    """
    Result of a property operation in Notion.
    
    Attributes:
        success: Whether the operation was successful
        property_name: Name of the affected property
        value: The value that was set or retrieved
        error: Error message, if any
        available_options: Available options for select-like properties
        api_response: The original API response
    """
    success: bool
    property_name: str
    value: Optional[Any] = None
    error: Optional[str] = None
    available_options: Optional[List[str]] = None
    api_response: Optional[Dict[str, Any]] = None
    
    # Common error messages
    NO_API_RESPONSE = "Failed to set property (no API response)"
    RELATION_TYPE_ERROR = "Property '{}' is of type 'relation'. Relations must be set using the RelationManager."
    
    @classmethod
    def from_success(cls, property_name: str, value: Any, api_response: Dict[str, Any]) -> "PropertyOperationResult":
        """Creates a success result."""
        return cls(
            success=True, 
            property_name=property_name, 
            value=value, 
            api_response=api_response
        )
    
    @classmethod
    def from_error(cls, property_name: str, 
                   error: str, 
                   value: Optional[Any] = None, 
                   available_options: Optional[List[str]] = None) -> "PropertyOperationResult":
        """Creates an error result."""
        return cls(
            success=False,
            property_name=property_name,
            value=value,
            error=error,
            available_options=available_options or []
        )
    
    @classmethod
    def from_api_error(cls, property_name: str, api_response: Dict[str, Any]) -> "PropertyOperationResult":
        """Creates a result from an API error response."""
        return cls(
            success=False,
            property_name=property_name,
            error=api_response.get("message", "Unknown API error"),
            api_response=api_response
        )
        
    @classmethod
    def from_no_api_response(cls, property_name: str, value: Optional[Any] = None) -> "PropertyOperationResult":
        """Creates a standardized result for missing API responses."""
        return cls.from_error(property_name, cls.NO_API_RESPONSE, value)

    @classmethod
    def from_relation_type_error(cls, property_name: str, value: Optional[Any] = None) -> "PropertyOperationResult":
        """Creates a standardized error result for relation type properties."""
        error_msg = cls.RELATION_TYPE_ERROR.format(property_name)
        return cls.from_error(property_name, error_msg, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the result to a dictionary."""
        result = {
            "success": self.success,
            "property": self.property_name,
        }
        
        if self.value is not None:
            result["value"] = self.value
        
        if not self.success:
            result["error"] = self.error
            
            if self.available_options:
                result["available_options"] = self.available_options
                
        if self.api_response:
            result["api_response"] = self.api_response
            
        return result
    
    def __str__(self) -> str:
        """String representation of the result."""
        if self.success:
            return f"Success: Property '{self.property_name}' set to '{self.value}'"
        
        if self.available_options:
            options = "', '".join(self.available_options)
            return f"Error: {self.error}\nAvailable options for '{self.property_name}': '{options}'"
        
        return f"Error: {self.error}"