from abc import ABCMeta, abstractmethod
import logging


_logger = logging.getLogger("touchstone")


class DatabaseBaseClass(metaclass=ABCMeta): # noqa
    def __init__(self, conn_url=None):
        _logger.debug("Initializing DatabaseBaseClass instance")
        if conn_url:
            self._conn_url = conn_url
        self._dict = None
        _logger.debug("Finished initializing DatabaseBaseClass instance")

    @abstractmethod
    def emit_compute_dict(self):
        pass
