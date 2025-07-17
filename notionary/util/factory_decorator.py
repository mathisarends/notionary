import functools
import inspect


def factory_only(*allowed_factories):
    """
    Decorator that ensures __init__ is only called from allowed factory methods.

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
                else:
                    raise RuntimeError(
                        f"Direct instantiation not allowed! Use one of: {', '.join(allowed_factories)}"
                    )
            finally:
                del frame

        return wrapper

    return decorator
