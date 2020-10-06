import logging
import elasticsearch
import json

from . import BenchmarkBaseClass

_logger = logging.getLogger("touchstone")


class Kubeburner(BenchmarkBaseClass):

    def _build_search(self):
        _logger.debug("Building search array for kube-burner")
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

    # The kuber-burner stores data for many prom queires and the index fields are not same for
    # all. This function helps us to compare if the given uuid's belong to same query and then
    # generate the bucket list for them.
    def check_valid_comparison(self):
        try:
            es = elasticsearch.Elasticsearch(self.conn_url, send_get_body_as='POST')
            search_object = {
                'query': {'match': {'uuid': self.uuid[0]}}}
            res = es.search(index='ripsaw-kube-burner', body=json.dumps(search_object))
            label1 = res['hits']['hits'][0]['_source']['labels']
            search_object = {
                'query': {'match': {'uuid': self.uuid[1]}}}
            res = es.search(index='ripsaw-kube-burner', body=json.dumps(search_object))
            label2 = res['hits']['hits'][0]['_source']['labels']
            isSame = True
            for label in label1:
                if label not in label2:
                    isSame = False

            if isSame is True:
                self.buckets = ['metricName.keyword']
                for label in label1:
                    self.buckets.append('labels.' + label + '.keyword')
            else:
                _logger.error("Provided UUID does not belong to the same query.")
        except Exception:
            _logger.error("Error connecting with Elastic server")

    def __init__(self, source_type=None, harness_type=None, uuid=None, conn_url=None):
        _logger.debug("Initializing kube-burner instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type,
                                    harness_type=harness_type)
        self.uuid = uuid
        self.conn_url = conn_url
        self.check_valid_comparison()
        self._search_dict = {
            'elasticsearch': {
                'metadata': {

                },
                'ripsaw': {
                    'ripsaw-kube-burner': {
                        'compare': ['uuid'],
                        'compute': [{
                            'filter': {},
                            'buckets': self.buckets,
                            'aggregations': {
                                'value': [{
                                    'percentiles': {
                                        'percents': [90, 99]
                                    }
                                }, 'avg', 'max', 'min']
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
        _logger.debug("Finished initializing kube-burner instance")

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
