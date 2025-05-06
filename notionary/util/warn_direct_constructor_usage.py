import functools
import inspect
from typing import Callable, Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])

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

        self._from_factory = False

        search_depth = min(6, len(stack))
        
        for i in range(1, search_depth):
            if i >= len(stack):
                break
                
            caller_frame = stack[i]
            caller_name = caller_frame.function
            
            # Debug logging might be helpful during development
            # print(f"Frame {i}: {caller_name}")
            
            # If called from a factory method, mark it and break
            if caller_name.startswith("create_from_") or caller_name.startswith("from_"):
                self._from_factory = True
                break

        # If not from factory, log warning
        if not self._from_factory and hasattr(self, "logger"):
            self.logger.warning(
                "Advisory: Direct constructor usage is discouraged. "
                "Consider using factory methods like create_from_page_id(), "
                "create_from_url(), or create_from_page_name() instead."
            )

        # Call the original __init__
        return func(self, *args, **kwargs)

    return cast(F, wrapper)