def singleton(cls):
    """
    Simple singleton decorator that ensures only one instance of a class exists.

    Usage:
        @singleton
        class MyClass:
            pass
    """
    instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in instances:
            instances[cls] = super(cls, cls).__new__(cls)
        return instances[cls]

    cls.__new__ = __new__
    return cls
