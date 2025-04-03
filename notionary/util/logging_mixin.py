import logging
import inspect

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

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
    def static_logger():
        stack = inspect.stack()
        for frame_info in stack[1:]:
            class_name = LoggingMixin._get_class_name_from_frame(frame_info.frame)
            if class_name:
                return logging.getLogger(class_name)
        return logging.getLogger("UnknownStaticContext")

    @staticmethod
    def _get_class_name_from_frame(frame):
        local_vars = frame.f_locals
        if 'self' in local_vars:
            return local_vars['self'].__class__.__name__
        
        if 'cls' in local_vars:
            return local_vars['cls'].__name__
        
        if '__qualname__' in frame.f_code.co_names:
            qualname = frame.f_code.co_qualname
            if '.' in qualname:
                return qualname.split('.')[0]
            
        return None