import functools
import inspect
import warnings


def factory_only(*allowed_factories):
    """
    Decorator that warns when __init__ is not called from allowed factory methods.

    Args:
        *allowed_factories: Names of allowed factory methods (e.g. 'from_database_id')
    """

    def decorator(init_method):
        @functools.wraps(init_method)
        def wrapper(self, *args, **kwargs):
            frame = inspect.currentframe()
            try:
                caller_frame = frame.f_back.f_back
                if not caller_frame:
                    return init_method(self, *args, **kwargs)
                caller_name = caller_frame.f_code.co_name
                if caller_name in allowed_factories or caller_name.startswith("_"):
                    return init_method(self, *args, **kwargs)

                warnings.warn(
                    f"Direct instantiation not recommended! Consider using one of: {', '.join(allowed_factories)}",
                    UserWarning,
                    stacklevel=3,
                )
                return init_method(self, *args, **kwargs)
            finally:
                del frame

        return wrapper

    return decorator
