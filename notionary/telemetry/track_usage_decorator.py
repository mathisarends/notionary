from functools import wraps
from typing import Any, Callable, Dict, Optional
from notionary.telemetry import NotionaryTelemetry


def track_usage(event_name: Optional[str] = None, properties: Optional[Dict[str, Any]] = None):
    """
    Simple decorator to track function usage.
    
    Args:
        event_name: Custom event name (defaults to function name)
        properties: Additional properties to track
        
    Usage:
        @track_usage()
        def my_function():
            pass
            
        @track_usage('custom_event_name')
        def my_function():
            pass
            
        @track_usage('custom_event', {'feature': 'advanced'})
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = NotionaryTelemetry()
            
            # Generate event name and properties
            event = event_name or _generate_event_name(func, args)
            event_properties = _build_properties(func, args, properties)
            
            # Track and execute
            telemetry.capture(event, event_properties)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def _get_class_name(func: Callable, args: tuple) -> Optional[str]:
    """Extract class name from function or arguments."""
    if args and hasattr(args[0], '__class__'):
        return args[0].__class__.__name__
    
    if hasattr(func, '__qualname__') and '.' in func.__qualname__:
        return func.__qualname__.split('.')[0]
    
    return None


def _generate_event_name(func: Callable, args: tuple) -> str:
    """Generate event name from function and class info."""
    class_name = _get_class_name(func, args)
    
    if class_name:
        return f"{class_name.lower()}_{func.__name__}_used"
    
    return f"{func.__name__}_used"


def _build_properties(func: Callable, args: tuple, properties: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Build event properties with function and class info."""
    event_properties = {
        'function_name': func.__name__,
        **(properties or {})
    }
    
    class_name = _get_class_name(func, args)
    if class_name:
        event_properties['class_name'] = class_name
    
    return event_properties