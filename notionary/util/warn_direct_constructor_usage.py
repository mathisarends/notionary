import functools
import inspect
from typing import Callable, Any, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])

def warn_direct_constructor_usage(func: F) -> F:
    """
    Method decorator that logs a warning when the constructor is called directly
    instead of through a factory method.
    
    This is an advisory decorator - it only logs a warning and doesn't
    prevent direct constructor usage.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Get the call stack
        stack = inspect.stack()
        
        # Default assumption: not from factory
        self._from_factory = False
        
        # Check if we have enough stack frames to determine the caller
        if len(stack) < 3:
            # Call the original __init__ and return early
            return func(self, *args, **kwargs)
            
        # Check if the call is from a factory method
        caller_frame = stack[2]
        caller_name = caller_frame.function
        
        # If called from a factory method, mark it and return
        if caller_name.startswith('create_from_') or caller_name.startswith('from_'):
            self._from_factory = True
            return func(self, *args, **kwargs)
        
        # If we got here, it's a direct constructor call - log a warning
        if hasattr(self, 'logger'):
            self.logger.warning(
                "Advisory: Direct constructor usage is discouraged. "
                "Consider using factory methods like create_from_page_id(), "
                "create_from_url(), or create_from_page_name() instead."
            )
            
        # Call the original __init__
        return func(self, *args, **kwargs)
    
    return cast(F, wrapper)