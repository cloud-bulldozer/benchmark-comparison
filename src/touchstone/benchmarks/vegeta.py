import logging


from . import BenchmarkBaseClass


_logger = logging.getLogger("touchstone")


class Vegeta(BenchmarkBaseClass):

    def _build_search(self):
        _logger.debug("Building search array for Vegeta")
        return self._search_dict[self._source_type][self._harness_type]

    def _build_search_metadata(self):
        return self._search_dict[self._source_type]["metadata"]

    def _build_compare_keys(self):
        _logger.debug("Building compare map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]['compare']
        return _temp_dict

    def _build_compute(self):
        _logger.debug("Building compute map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]['compute']
        return _temp_dict

    def __init__(self, source_type=None, harness_type=None):
        _logger.debug("Initializing Vegeta instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type,
                                    harness_type=harness_type)
        self._search_dict = {
            'elasticsearch': {
                'metadata': {
                    'cpuinfo-metadata': {
                        'element': 'pod_name',
                        'compare': ['value.Model name', 'value.Architecture',
                                    'value.CPU(s)'],
                    },
                    'meminfo-metadata': {
                        'element': 'pod_name',
                        'compare': ['value.MemTotal', 'value.Active'],
                    },
                },
                'ripsaw': {
                    'ripsaw-vegeta-results': {
                        'compare': ['uuid', 'user', 'cluster_name',
                                    'hostname', 'duration',
                                    'workers', 'requests'],
                        'compute': [{
                            'filter': {},
                            'buckets': ['targets.keyword'],
                            'aggregations': {
                                'rps': ['avg'],
                                'throughput': ['avg'],
                                'req_latency': ['avg'],
                                'p95_latency': ['avg'],
                                'p99_latency': ['avg'],
                                'max_latency': ['avg'],
                                'min_latency': ['avg'],
                                'bytes_in': ['avg'],
                                'bytes_out': ['avg'],
                            },
                            'collate': []
                        }, ],
                    },
                },
            },
        }
        self._search_map = self._build_search()
        self._search_map_metadata = self._build_search_metadata()
        self._compute_map = self._build_compute()
        self._compare_map = self._build_compare_keys()
        _logger.debug("Finished initializing Vegeta instance")

    def emit_compute_map(self):
        _logger.debug("Emitting built compute map ")
        _logger.info("Compute map is {} in the database \
                     {}".format(self._compute_map, self._source_type))
        return self._compute_map

    def emit_compare_map(self):
        _logger.debug("Emitting built compare map ")
        _logger.info("compare map is {} in the database \
                     {}".format(self._compare_map, self._source_type))
        return self._compare_map

    def emit_indices(self):
        return self._search_map.keys()

    def emit_metadata_search_map(self):
        return self._search_map_metadata
