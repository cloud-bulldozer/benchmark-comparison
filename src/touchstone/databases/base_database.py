from abc import ABCMeta, abstractmethod
import logging


_logger = logging.getLogger("touchstone")

class DatabaseBaseClass(metaclass=ABCMeta):
    def __init__(self, conn_url=None):
        _logger.debug("Initializing DatabaseBaseClass instance")
        if conn_url:
            self._conn_url = conn_url
        self._dict = None
        print(self._conn_url)
        _logger.debug("Finished initializing DatabaseBaseClass instance")

    @abstractmethod
    def emit_values_dict(self):
        pass
