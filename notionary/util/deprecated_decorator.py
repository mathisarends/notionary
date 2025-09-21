import functools
import logging
import warnings
from collections.abc import Callable
from typing import Any


def deprecated(
    message: str | None = None, logger: logging.Logger | None = None
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Logger resolution with LoggingMixin support
            log = logger

            if not log and args:
                # Try instance logger first (for instance methods)
                if hasattr(args[0], "instance_logger"):
                    log = args[0].instance_logger
                # Try class logger (for class methods)
                elif hasattr(args[0], "logger"):
                    log = args[0].logger

            # Fallback to module logger
            if not log:
                log = logging.getLogger(func.__module__)

            # Create deprecation message
            if message:
                deprecation_msg = f"Method '{func.__name__}' is deprecated: {message}"
            else:
                deprecation_msg = f"Method '{func.__name__}' is deprecated and will be removed in a future version."

            log.warning(deprecation_msg)
            warnings.warn(deprecation_msg, DeprecationWarning, stacklevel=2)

            return func(*args, **kwargs)

        return wrapper

    return decorator
