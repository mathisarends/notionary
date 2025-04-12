from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class RelationOperationResult:
    """
    Result of a relation operation in Notion.
    
    Attributes:
        success: Whether the operation was successful overall
        property_name: Name of the affected relation property
        found_pages: List of page titles/IDs that were successfully found
        not_found_pages: List of page titles that could not be found
        page_ids_added: List of page IDs that were added to the relation
        error: Error message, if any
        api_response: The original API response
    """
    success: bool
    property_name: str
    found_pages: List[str] = field(default_factory=list)
    not_found_pages: List[str] = field(default_factory=list)
    page_ids_added: List[str] = field(default_factory=list)
    error: Optional[str] = None
    api_response: Optional[Dict[str, Any]] = None
    
    NO_API_RESPONSE = "Failed to update relation (no API response)"
    NO_PAGES_FOUND = "No valid pages found for relation"
    
    @classmethod
    def from_success(cls, property_name: str, 
                     found_pages: List[str], 
                     page_ids_added: List[str], 
                     api_response: Dict[str, Any],
                     not_found_pages: Optional[List[str]] = None) -> "RelationOperationResult":
        """Creates a success result."""
        return cls(
            success=True, 
            property_name=property_name,
            found_pages=found_pages,
            not_found_pages=not_found_pages or [],
            page_ids_added=page_ids_added,
            api_response=api_response
        )
    
    @classmethod
    def from_error(cls, property_name: str, 
                  error: str,
                  found_pages: Optional[List[str]] = None,
                  not_found_pages: Optional[List[str]] = None,
                  page_ids_added: Optional[List[str]] = None) -> "RelationOperationResult":
        """Creates an error result."""
        return cls(
            success=False,
            property_name=property_name,
            found_pages=found_pages or [],
            not_found_pages=not_found_pages or [],
            page_ids_added=page_ids_added or [],
            error=error
        )
    
    @classmethod
    def from_no_pages_found(cls, property_name: str, 
                            not_found_pages: List[str]) -> "RelationOperationResult":
        """Creates a standardized result for when no pages were found."""
        return cls.from_error(
            property_name=property_name,
            error=cls.NO_PAGES_FOUND,
            not_found_pages=not_found_pages
        )

    @classmethod
    def from_no_api_response(cls, property_name: str, 
                            found_pages: List[str],
                            page_ids_added: List[str]) -> "RelationOperationResult":
        """Creates a standardized result for a missing API response."""
        return cls.from_error(
            property_name=property_name,
            error=cls.NO_API_RESPONSE,
            found_pages=found_pages,
            page_ids_added=page_ids_added
        )
    
    @property
    def has_not_found_pages(self) -> bool:
        """Returns True if there were any pages that couldn't be found."""
        return len(self.not_found_pages) > 0
    
    @property
    def has_found_pages(self) -> bool:
        """Returns True if any pages were found."""
        return len(self.found_pages) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the result to a dictionary."""
        result = {
            "success": self.success,
            "property": self.property_name,
        }
        
        if self.found_pages:
            result["found_pages"] = self.found_pages
            
        if self.not_found_pages:
            result["not_found_pages"] = self.not_found_pages
            
        if self.page_ids_added:
            result["page_ids_added"] = self.page_ids_added
        
        if not self.success:
            result["error"] = self.error
            
        if self.api_response:
            result["api_response"] = self.api_response
            
        return result
    
    def __str__(self) -> str:
        """String representation of the result."""
        if self.success:
            base = f"Success: Added {len(self.page_ids_added)} relation(s) to property '{self.property_name}'"
            
            if self.not_found_pages:
                pages_str = "', '".join(self.not_found_pages)
                base += f"\nWarning: Could not find pages: '{pages_str}'"
                
            return base
        
        if not self.found_pages and self.not_found_pages:
            pages_str = "', '".join(self.not_found_pages)
            return f"Error: {self.error}\nNone of the requested pages were found: '{pages_str}'"
        
        if self.found_pages and not self.page_ids_added:
            return f"Error: {self.error}\nPages were found but could not be added to the relation."
            
        return f"Error: {self.error}"