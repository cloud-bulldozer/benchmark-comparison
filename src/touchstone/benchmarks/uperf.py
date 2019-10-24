import logging


from . import BenchmarkBaseClass


_logger = logging.getLogger("touchstone")

class Uperf(BenchmarkBaseClass):

    def _build_search(self):
        _logger.debug("Building search array for uperf")
        return self._search_dict[self._source_type][self._harness_type]

    def __init__(self, source_type=None, harness_type=None):
        _logger.debug("Initializing uperf instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type, harness_type=harness_type)
        self._search_dict = {'elasticsearch': { 'ripsaw': {'ripsaw-uperf-results': {'buckets':['test_type.keyword','protocol.keyword','message_size','num_threads'], 'aggregations': ['norm_byte','norm_ops','norm_ltcy'], 'compare':['uuid','user','cluster_name','hostnetwork','service_ip']}} }}
        self._search_map = self._build_search()
        _logger.debug("Finished initializing uperf instance")

    def emit_search_map(self):
        _logger.debug("Emitting built search map ")
        _logger.info("Search map is {} in the database {}".format(self._search_map,self._source_type))
        return self._search_map
