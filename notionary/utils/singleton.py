from collections.abc import Callable
from typing import Any


def singleton(cls) -> Callable[..., Any]:
    instances = {}

    def get_instance(*args, **kwargs) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
