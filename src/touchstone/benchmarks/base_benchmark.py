from abc import ABCMeta, abstractmethod
import logging
import json


_logger = logging.getLogger("touchstone")


class BenchmarkBaseClass(metaclass=ABCMeta):  # noqa
    def __init__(self, source_type=None, harness_type=None, config=None):
        _logger.debug("Initializing BenchmarkBaseClass instance")
        self.benchmark_cfg = None
        if source_type:
            self._source_type = source_type
        if harness_type:
            self._harness_type = harness_type
        if config:
            self.benchmark_cfg = json.load(config)
        self._indices_map = None
        _logger.debug("Finished initializing BenchmarkBaseClass instance")

    @abstractmethod
    def emit_compute_map(self):
        pass

    @abstractmethod
    def emit_indices(self):
        pass
