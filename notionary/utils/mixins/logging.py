import logging
import os
from typing import ClassVar


def _setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)


_setup_logging()


class LoggingMixin:
    logger: ClassVar[logging.Logger] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.logger = logging.getLogger(cls.__name__)

    @property
    def instance_logger(self) -> logging.Logger:
        """Instance logger - for instance methods"""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    @staticmethod
    def _get_class_name_from_frame(frame) -> str | None:
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
