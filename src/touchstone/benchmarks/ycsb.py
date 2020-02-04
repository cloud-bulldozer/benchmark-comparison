import logging


from . import BenchmarkBaseClass


_logger = logging.getLogger("touchstone")


class Ycsb(BenchmarkBaseClass):

    def _build_search(self):
        _logger.debug("Building search array for YCSB")
        return self._search_dict[self._source_type][self._harness_type]

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
        _logger.debug("Initializing YCSB instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type,
                                    harness_type=harness_type)
        self._search_dict = {
          'elasticsearch': {
            'ripsaw': {
              'ripsaw-ycsb-summary': {
                'compare': ['uuid', 'user','recordcount','operationcount','driver'],
                'compute': [{
                  'filter': {
                    'workload_type': 'workloada',
                    'phase': 'run'
                  },
                  'buckets': ['iteration'],
                  'aggregations': {},
                  'collate': ['data.READ.95thPercentileLatency(us)',
                              'data.OVERALL.Throughput(ops/sec)',
                              'data.UPDATE.95thPercentileLatency(us)']
                  },
                  {
                    'filter': {
                      'workload_type': 'workloadb',
                      'phase': 'run'
                    },
                    'buckets': ['iteration'],
                    'aggregations': {},
                    'collate': ['data.READ.95thPercentileLatency(us)',
                                'data.OVERALL.Throughput(ops/sec)',
                                'data.UPDATE.95thPercentileLatency(us)']
                  },
                  {
                    'filter': {
                      'workload_type': 'workloadc',
                      'phase': 'run'
                    },
                    'buckets': ['iteration'],
                    'aggregations': {},
                    'collate': ['data.READ.95thPercentileLatency(us)',
                                'data.OVERALL.Throughput(ops/sec)']
                  },
                  {
                    'filter': {
                      'workload_type': 'workloadd',
                      'phase': 'run'
                    },
                    'buckets': ['iteration'],
                    'aggregations': {},
                    'collate': ['data.INSERT.95thPercentileLatency(us)',
                                'data.OVERALL.Throughput(ops/sec)',
                                'data.READ.95thPercentileLatency(us)']
                  },
                  {
                    'filter': {
                      'workload_type': 'workloade',
                      'phase': 'run'
                    },
                    'buckets': ['iteration'],
                    'aggregations': {},
                    'collate': ['data.OVERALL.Throughput(ops/sec)']
                  },
                  {
                    'filter': {
                      'workload_type': 'workloadf',
                      'phase': 'run'
                    },
                    'buckets': ['iteration'],
                    'aggregations': {},
                    'collate': ['data.READ-MODIFY-WRITE.95thPercentileLatency(us)',
                                'data.OVERALL.Throughput(ops/sec)',
                                'data.READ.95thPercentileLatency(us)',
                                'data.UPDATE.95thPercentileLatency(us)']
                  },
                ]
              }
            }
          }
        }
        self._search_map = self._build_search()
        self._compute_map = self._build_compute()
        self._compare_map = self._build_compare_keys()
        _logger.debug("Finished initializing ycsb instance")

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
