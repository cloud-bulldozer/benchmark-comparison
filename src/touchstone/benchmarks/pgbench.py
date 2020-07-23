import logging


from . import BenchmarkBaseClass


_logger = logging.getLogger("touchstone")


class Pgbench(BenchmarkBaseClass):

    def _build_search(self):
        _logger.debug("Building search array for PGBENCH")
        return self._search_dict[self._source_type][self._harness_type]

    def _build_search_metadata(self):
        return self._search_dict[self._source_type]["metadata"]
    
    def _build_compare_keys(self):
        _logger.debug("Building compare map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]['compare']
        return _temp_dict

    def _build_compare_keys_metadata(self):
        _logger.debug("Building compare map for metadata")
        _temp_dict = {}
        for index in self._search_map_metadata:
            _temp_dict[index] = self._search_map_metadata[index]['compare']
        return _temp_dict
    
    def _build_compute(self):
        _logger.debug("Building compute map")
        _temp_dict = {}
        for index in self._search_map:
            _temp_dict[index] = self._search_map[index]['compute']
        return _temp_dict

    def __init__(self, source_type=None, harness_type=None):
        _logger.debug("Initializing PGBENCH instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type,
                                    harness_type=harness_type)
        self._search_dict = {
            'elasticsearch': {
                'metadata': {
                    'cpuinfo-metadata': { 
                        'element': 'pod_name',
                        'compare': ['Model name', 'Architecture', 'CPU(s)', 'Hypervisor vendor']
                    },
                    'meminfo-metadata': { 
                        'element': 'pod_name',
                        'compare': ['MemTotal', 'Active'],
                    },
                },
                'ripsaw': { 
                    'ripsaw-pgbench-summary': {
                        'compare': ['uuid', 'user', 'cluster_name',
                                    'scaling_factor', 'query_mode',
                                    'number_of_threads', 'number_of_clients',
                                    'duration_seconds'
                                    ],
                        'compute': [{
                            'filter': {
                                'workload': 'pgbench'
                            },
                            'buckets': ['iteration'],
                            'aggregations': {},
                            'collate': ['tps_incl_con_est',
                                        'number_of_transactions_actually_processed', # noqa
                                        'latency_average_ms'
                                       ]
                        }, ]
                    },
                    'ripsaw-pgbench-results': {
                        'compare': ['transaction_type'],
                        'compute': [{
                            'filter': {
                                'workload': 'pgbench'
                            },
                            'buckets': ['iteration'],
                            'aggregations': {
                                'latency_ms': [{
                                    'percentiles': {
                                        'percents': [95]
                                    }
                                }]
                            },
                            'collate': []
                        }, ]
                    }
                }
            }
        }
        self._search_map = self._build_search()
        self._search_map_metadata = self._build_search_metadata()
        self._compute_map = self._build_compute()
        self._compare_map = self._build_compare_keys()
        self._compare_map_metadata = self._build_compare_keys_metadata()
        _logger.debug("Finished initializing pgbench instance")

    def emit_compute_map(self):
        _logger.debug("Emitting built compute map ")
        _logger.info("Compute map is {} in the database \
                     {}".format(self._compute_map, self._source_type))
        return self._compute_map

    def emit_compare_map_metadata(self):
        _logger.debug("Emitting built metadata compare map ")
        _logger.info("compare map is {} in the database \
                     {}".format(self._compare_map_metadata, self._source_type))
        return self._compare_map_metadata

    def emit_compare_map(self):
        _logger.debug("Emitting built compare map ")
        _logger.info("compare map is {} in the database \
                     {}".format(self._compare_map, self._source_type))
        return self._compare_map

    def emit_indices(self):
        return self._search_map.keys()

    def emit_indices_metadata(self):
        return self._search_map_metadata.keys()

    def emit_metadata_search_map(self):
        return self._search_map_metadata