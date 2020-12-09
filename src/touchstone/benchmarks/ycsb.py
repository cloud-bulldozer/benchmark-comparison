import logging


from . import BenchmarkBaseClass


logger = logging.getLogger("touchstone")


class Ycsb(BenchmarkBaseClass):
    def _build_search(self):
        logger.debug("Building search array for YCSB")
        return self._search_dict[self._source_type][self._harness_type]

    def _build_search_metadata(self):
        return self._search_dict[self._source_type]["metadata"]

    def _build_compute(self):
        logger.debug("Building compute map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]
        return _temp_dict

    def __init__(self, source_type=None, harness_type=None, config=None):
        logger.debug("Initializing YCSB instance")
        BenchmarkBaseClass.__init__(
            self, source_type=source_type, harness_type=harness_type, config=config
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
                    "ripsaw-ycsb-summary": [
                        {
                            "filter": {"phase": "run", "workload_type": "workloada"},
                            "buckets": [
                                "iteration",
                                "recordcount",
                                "operationcount",
                                "driver.keyword",
                            ],
                            "aggregations": {
                                "data.OVERALL.Throughput(ops/sec)": ["max"],
                                "data.UPDATE.95thPercentileLatency(us)": ["max"],
                                "data.READ.95thPercentileLatency(us)": ["max"],
                            },
                        },
                        {
                            "filter": {"phase": "run", "workload_type": "workloadb"},
                            "buckets": [
                                "iteration",
                                "recordcount",
                                "operationcount",
                                "driver.keyword",
                            ],
                            "aggregations": {
                                "data.OVERALL.Throughput(ops/sec)": ["max"],
                                "data.READ.95thPercentileLatency(us)": ["max"],
                                "data.UPDATE.95thPercentileLatency(us)": ["max"],
                            },
                        },
                        {
                            "filter": {"phase": "run", "workload_type": "workloadc"},
                            "buckets": [
                                "iteration",
                                "recordcount",
                                "operationcount",
                                "driver.keyword",
                            ],
                            "aggregations": {
                                "data.OVERALL.Throughput(ops/sec)": ["max"],
                                "data.READ.95thPercentileLatency(us)": ["max"],
                            },
                        },
                        {
                            "filter": {"phase": "run", "workload_type": "workloadd"},
                            "buckets": [
                                "iteration",
                                "recordcount",
                                "operationcount",
                                "driver.keyword",
                            ],
                            "aggregations": {
                                "data.OVERALL.Throughput(ops/sec)": ["max"],
                                "data.INSERT.95thPercentileLatency(us)": ["max"],
                                "data.READ.95thPercentileLatency(us)": ["max"],
                            },
                        },
                        {
                            "filter": {"phase": "run", "workload_type": "workloade"},
                            "buckets": [
                                "iteration",
                                "recordcount",
                                "operationcount",
                                "driver.keyword",
                            ],
                            "aggregations": {
                                "data.OVERALL.Throughput(ops/sec)": ["max"]
                            },
                        },
                        {
                            "filter": {"phase": "run", "workload_type": "workloadf"},
                            "buckets": [
                                "iteration",
                                "recordcount",
                                "operationcount",
                                "driver.keyword",
                            ],
                            "aggregations": {
                                "data.OVERALL.Throughput(ops/sec)": ["max"],
                                "data.READ-MODIFY-WRITE.95thPercentileLatency(us)": [
                                    "max"
                                ],
                                "data.READ.95thPercentileLatency(us)": ["max"],
                                "data.UPDATE.95thPercentileLatency(us)": ["max"],
                            },
                        },
                    ],
                },
            }
        }
        if self.benchmark_cfg:
            self._search_dict = self.benchmark_cfg
        self._search_map = self._build_search()
        self._search_map_metadata = self._build_search_metadata()
        self._compute_map = self._build_compute()
        logger.debug("Finished initializing ycsb instance")

    def emit_compute_map(self):
        logger.debug("Emitting built compute map ")
        logger.info(
            "Compute map is {} in the database \
                     {}".format(
                self._compute_map, self._source_type
            )
        )
        return self._compute_map

    def emit_indices(self):
        return self._search_map.keys()

    def emit_metadata_search_map(self):
        return self._search_map_metadata
