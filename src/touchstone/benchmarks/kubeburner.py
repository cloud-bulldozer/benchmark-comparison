import logging


from . import BenchmarkBaseClass


logger = logging.getLogger("touchstone")


class Kubeburner(BenchmarkBaseClass):
    def _build_search(self):
        logger.debug("Building search array for kubeburner")
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
        logger.debug("Initializing kubeburner instance")
        BenchmarkBaseClass.__init__(
            self, source_type=source_type, harness_type=harness_type
        )
        self._search_dict = {
            "elasticsearch": {
                "metadata": {},
                "ripsaw": {
                    "ripsaw-kube-burner": {
                        "compare": ["uuid"],
                        "compute": [
                            {
                                "filter": {"metricName.keyword": "podLatencyQuantilesMeasurement"},
                                "buckets": ["quantileName.keyword"],
                                "aggregations": {
                                    "P99": ["avg"],
                                },
                            },
                            {
                                "filter": {},
                                "exclude": [
                                    {"metricName.keyword": "podLatencyMeasurement"},
                                    {"metricName.keyword": "podLatencyQuantilesMeasurement"},
                                    {"metricName.keyword": "jobSummary"}

                                ],
                                "buckets": ["metricName.keyword"],
                                "aggregations": {"value": ["avg"]},
                            }
                        ],
                    },
                },
            },
        }

        self._search_map = self._build_search()
        self._search_map_metadata = self._build_search_metadata()
        self._compute_map = self._build_compute()
        self._compare_map = self._build_compare_keys()
        logger.debug("Finished initializing kubeburner instance")

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
