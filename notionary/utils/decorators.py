import asyncio
import functools
import logging
import time
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def time_execution_async(
    additional_text: str = "",
    threshold: float = 0.25,
) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
    def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time

            if _should_log_execution(execution_time, threshold):
                logger = _get_logger_from_context(args, func)
                function_name = additional_text.strip("-") or func.__name__
                logger.info(f"⏳ {function_name}() took {execution_time:.2f}s")

            return result

        return wrapper

    return decorator


def _should_log_execution(execution_time: float, threshold: float) -> bool:
    return execution_time > threshold


def _get_logger_from_context(args: tuple, func: Callable) -> logging.Logger:
    if _has_instance_logger(args):
        return _extract_instance_logger(args)

    return _get_module_logger(func)


def _has_instance_logger(args: tuple) -> bool:
    return bool(args) and hasattr(args[0], "logger")


def _extract_instance_logger(args: tuple) -> logging.Logger:
    return args[0].logger


def _get_module_logger(func: Callable) -> logging.Logger:
    return logging.getLogger(func.__module__)


def async_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: tuple[type[Exception], ...] | None = None,
):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # If specific exceptions are defined, only retry those
                    if retry_on_exceptions is not None and not isinstance(e, retry_on_exceptions):
                        raise

                    if attempt == max_retries:
                        raise

                    await asyncio.sleep(delay)
                    delay *= backoff_factor

            raise last_exception

        return wrapper

    return decorator
