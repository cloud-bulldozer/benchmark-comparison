import logging
import json


logger = logging.getLogger("touchstone")


class Benchmark:
    def __init__(self, config, source_type):
        try:
            self.benchmark_config = json.load(config)
        except Exception as err:
            logger.critical(f"Config parsing error {err}")
            exit(1)
        self.source_type = source_type
        self._search_map = self.benchmark_config[self.source_type]
        self.search_map_metadata = {}
        if "metadata" in self.benchmark_config[self.source_type]:
            self.search_map_metadata = self.benchmark_config[self.source_type].pop("metadata")
        self.compute_map = self._build_compute()

    def _build_compute(self):
        logger.debug("Building compute map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]
        return _temp_dict

    def get_indices(self):
        return self._search_map.keys()
