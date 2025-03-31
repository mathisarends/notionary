import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
setup_logging()

class LoggingMixin:
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    @classmethod
    def class_logger(cls):
        """Class logger - für Klassenmethoden"""
        return logging.getLogger(cls.__name__)
    
    @staticmethod
    def static_logger(class_name):
        """Static logger - für statische Methoden"""
        return logging.getLogger(class_name)