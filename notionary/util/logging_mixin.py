import logging
import inspect
from typing import Optional, ClassVar


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


setup_logging()


class LoggingMixin:
    # Class attribute with proper typing
    logger: ClassVar[logging.Logger] = None

    def __init_subclass__(cls, **kwargs):
        """
        This method is called when a class inherits from LoggingMixin.
        It automatically sets up the logger as a class attribute.
        """
        super().__init_subclass__(**kwargs)
        cls.logger = logging.getLogger(cls.__name__)

    @property
    def instance_logger(self) -> logging.Logger:
        """Instance logger - for instance methods"""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    @staticmethod
    def static_logger() -> logging.Logger:
        """Static logger - for static methods"""
        stack = inspect.stack()
        for frame_info in stack[1:]:
            class_name = LoggingMixin._get_class_name_from_frame(frame_info.frame)
            if class_name:
                return logging.getLogger(class_name)
        return logging.getLogger("UnknownStaticContext")

    @staticmethod
    def _get_class_name_from_frame(frame) -> Optional[str]:
        local_vars = frame.f_locals
        if "self" in local_vars:
            return local_vars["self"].__class__.__name__

        if "cls" in local_vars:
            return local_vars["cls"].__name__

        if "__qualname__" in frame.f_code.co_names:
            qualname = frame.f_code.co_qualname
            if "." in qualname:
                return qualname.split(".")[0]

        return None
