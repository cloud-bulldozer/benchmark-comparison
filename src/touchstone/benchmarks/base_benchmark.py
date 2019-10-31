from abc import ABCMeta, abstractmethod
import logging


_logger = logging.getLogger("touchstone")


class BenchmarkBaseClass(metaclass=ABCMeta): # noqa
    def __init__(self, source_type=None, harness_type=None):
        _logger.debug("Initializing BenchmarkBaseClass instance")
        if source_type:
            self._source_type = source_type
        if harness_type:
            self._harness_type = harness_type
        self._indices_map = None
        _logger.debug("Finished initializing BenchmarkBaseClass instance")

    @abstractmethod
    def emit_compute_map(self):
        pass

    @abstractmethod
    def emit_compare_map(self):
        pass

    @abstractmethod
    def emit_indices(self):
        pass
