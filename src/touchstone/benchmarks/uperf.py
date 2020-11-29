import logging


from . import BenchmarkBaseClass


logger = logging.getLogger("touchstone")


class Uperf(BenchmarkBaseClass):
    def _build_search(self):
        logger.debug("Building search array for uperf")
        return self._search_dict[self._source_type][self._harness_type]

    def _build_search_metadata(self):
        return self._search_dict[self._source_type]["metadata"]

    def _build_compare_keys(self):
        logger.debug("Building compare map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]["compare"]
        return _temp_dict

    def _build_compute(self):
        logger.debug("Building compute map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]["compute"]
        return _temp_dict

    def __init__(self, source_type=None, harness_type=None):
        logger.debug("Initializing uperf instance")
        BenchmarkBaseClass.__init__(
            self, source_type=source_type, harness_type=harness_type
        )
        self._search_dict = {
            "elasticsearch": {
                "metadata": {
                    "cpuinfo-metadata": {
                        "element": "pod_name",
                        "compare": [
                            "value.Model name",
                            "value.Architecture",
                            "value.CPU(s)",
                        ],
                    },
                    "meminfo-metadata": {
                        "element": "pod_name",
                        "compare": ["value.MemTotal"],
                    },
                },
                "ripsaw": {
                    "ripsaw-uperf-results": {
                        "compare": [
                            "uuid",
                            "user",
                            "cluster_name",
                            "hostnetwork",
                            "service_ip",
                        ],
                        "compute": [
                            {
                                "filter": {"test_type.keyword": "stream"},
                                "exclude": {"norm_ops": 0},
                                "buckets": [
                                    "protocol.keyword",
                                    "message_size",
                                    "num_threads",
                                ],
                                "aggregations": {
                                    "norm_byte": [
                                        "max",
                                        "avg",
                                        {"percentiles": {"percents": [50]}},  # noqa
                                    ]
                                },
                            },
                            {
                                "filter": {"test_type.keyword": "rr"},
                                "exclude": {"norm_ops": 0},
                                "buckets": [
                                    "protocol.keyword",
                                    "message_size",
                                    "num_threads",
                                ],
                                "aggregations": {
                                    "norm_ops": ["max", "avg"],
                                    "norm_ltcy": [
                                        {"percentiles": {"percents": [90, 99]}},
                                        "avg",
                                    ],
                                },
                            },
                        ],
                    }
                },
            }
        }
        self._search_map = self._build_search()
        self._search_map_metadata = self._build_search_metadata()
        self._compute_map = self._build_compute()
        self._compare_map = self._build_compare_keys()
        logger.debug("Finished initializing uperf instance")

    def emit_compute_map(self):
        logger.debug("Emitting built compute map ")
        logger.info(
            "Compute map is {} in the database \
                     {}".format(
                self._compute_map, self._source_type
            )
        )
        return self._compute_map

    def emit_compare_map(self):
        logger.debug("Emitting built compare map ")
        logger.info(
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
