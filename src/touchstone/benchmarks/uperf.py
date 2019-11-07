import logging


from . import BenchmarkBaseClass


_logger = logging.getLogger("touchstone")


class Uperf(BenchmarkBaseClass):

    def _build_search(self):
        _logger.debug("Building search array for uperf")
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
        _logger.debug("Initializing uperf instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type,
                                    harness_type=harness_type)
        self._search_dict = {
          'elasticsearch': {
            'ripsaw': {
              'ripsaw-uperf-results': {
                'compare': ['uuid', 'user', 'cluster_name',
                  'hostnetwork', 'service_ip'
                ],
                'compute': [{
                  'filter': {
                    'test_type.keyword': 'stream'
                  },
                  'buckets': ['protocol.keyword',
                    'message_size', 'num_threads'
                  ],
                  'aggregations': {
                    'norm_byte': ['max', 'avg']
                  }
                }, {
                  'filter': {
                    'test_type.keyword': 'rr'
                  },
                  'buckets': ['protocol.keyword',
                    'message_size', 'num_threads'
                  ],
                  'aggregations': {
                    'norm_ops': ['max', 'avg'],
                    'norm_ltcy': [{
                      'percentiles': {
                        'percents': [90, 99]
                      }
                    }, 'avg']
                  },
                }]
              }
            }
          }
        }
        self._search_map = self._build_search()
        self._compute_map = self._build_compute()
        self._compare_map = self._build_compare_keys()
        _logger.debug("Finished initializing uperf instance")

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
