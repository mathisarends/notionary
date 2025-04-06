from typing import TypeVar
from functools import wraps

T = TypeVar('T')

def singleton(cls: T) -> T:
    """
    Decorator zur Implementierung des Singleton-Musters.
    Stellt sicher, dass nur eine Instanz der Klasse existiert.
    """
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance
