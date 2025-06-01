from typing import TypeVar, Dict, Any, Type, cast

T = TypeVar('T')

class SingletonMetaClass(type):
    """
    A metaclass that ensures a class has only a single instance.
    Provides a get_instance() method with proper type hinting.
    """
    _instances: Dict[Type, Any] = {}

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """Called when the class is instantiated (e.g., MyClass())."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cast(T, cls._instances[cls])

    def get_instance(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """Explicit method to retrieve the singleton instance with correct return type."""
        return cls(*args, **kwargs)  # Triggers __call__