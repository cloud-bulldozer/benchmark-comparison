import logging


from . import BenchmarkBaseClass


_logger = logging.getLogger("touchstone")


class Mb(BenchmarkBaseClass):
    def _build_search(self):
        _logger.debug("Building search array for Mb")
        return self._search_dict[self._source_type][self._harness_type]

    def _build_search_metadata(self):
        return self._search_dict[self._source_type]["metadata"]

    def _build_compare_keys(self):
        _logger.debug("Building compare map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]["compare"]
        return _temp_dict

    def _build_compute(self):
        _logger.debug("Building compute map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]["compute"]
        return _temp_dict

    def __init__(self, source_type=None, harness_type=None):
        _logger.debug("Initializing Mb instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type, harness_type=harness_type)
        self._search_dict = {
            "elasticsearch": {
                "metadata": {
                    "cpuinfo-metadata": {
                        "element": "pod_name",
                        "compare": ["value.Model name", "value.Architecture", "value.CPU(s)"],
                    },
                    "meminfo-metadata": {
                        "element": "pod_name",
                        "compare": ["value.MemTotal", "value.Active"],
                    },
                },
                "ripsaw": {
                    "router-test-results": {
                        "compare": [
                            "uuid",
                            "tls_reuse",
                            "test_name",
                            "num_workload_generators",
                            "delay",
                            "runtime",
                        ],
                        "compute": [
                            {
                                "filter": {"test_type": "http"},
                                "buckets": ["routes", "conn_per_targetroute", "keepalive"],
                                "aggregations": {"requests_per_second": ["avg"], "latency_95pctl": ["avg"]},
                                "collate": [],
                            },
                            {
                                "filter": {"test_type": "edge"},
                                "buckets": ["routes", "conn_per_targetroute", "keepalive"],
                                "aggregations": {"requests_per_second": ["avg"], "latency_95pctl": ["avg"]},
                                "collate": [],
                            },
                            {
                                "filter": {"test_type": "passthrough"},
                                "buckets": ["routes", "conn_per_targetroute", "keepalive"],
                                "aggregations": {"requests_per_second": ["avg"], "latency_95pctl": ["avg"]},
                                "collate": [],
                            },
                            {
                                "filter": {"test_type": "reencrypt"},
                                "buckets": ["routes", "conn_per_targetroute", "keepalive"],
                                "aggregations": {"requests_per_second": ["avg"], "latency_95pctl": ["avg"]},
                                "collate": [],
                            },
                            {
                                "filter": {"test_type": "mix"},
                                "buckets": ["routes", "conn_per_targetroute", "keepalive"],
                                "aggregations": {"requests_per_second": ["avg"], "latency_95pctl": ["avg"]},
                                "collate": [],
                            },
                        ],
                    },
                },
            },
        }
        self._search_map = self._build_search()
        self._search_map_metadata = self._build_search_metadata()
        self._compute_map = self._build_compute()
        self._compare_map = self._build_compare_keys()
        _logger.debug("Finished initializing Mb instance")

    def emit_compute_map(self):
        _logger.debug("Emitting built compute map ")
        _logger.info(
            "Compute map is {} in the database \
                     {}".format(
                self._compute_map, self._source_type
            )
        )
        return self._compute_map

    def emit_compare_map(self):
        _logger.debug("Emitting built compare map ")
        _logger.info(
            "compare map is {} in the database \
                     {}".format(
                self._compare_map, self._source_type
            )
        )
        return self._compare_map

    def emit_indices(self):
        return self._search_map.keys()

    def emit_metadata_search_map(self):
        return self._search_map_metadata
