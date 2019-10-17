import logging


from . import BenchmarkBaseClass


_logger = logging.getLogger("touchstone")

class Uperf(BenchmarkBaseClass):

    def _build_indices(self):
        _logger.debug("Building indices array for uperf")
        return self._indices_dict[self._source_type][self._harness_type]

    def __init__(self, source_type=None, harness_type=None):
        _logger.debug("Initializing uperf instance")
        BenchmarkBaseClass.__init__(self, source_type=source_type, harness_type=harness_type)
        self._indices_dict = {'elasticsearch': { 'ripsaw': {'indices': ['ripsaw-uperf-results'], 'buckets':['test_type','protocol','message_size','num_threads'], 'aggregations': ['norm_byte','norm_ops','norm_ltcy'], 'compare':['uuid','user','cluster_name','hostnetwork','serviceip']} }}
        self._indices_array = self._build_indices()
        _logger.debug("Finished initializing uperf instance")

    def _emit_indices(self):
        _logger.debug("Emitting built indices array")
        _logger.info("Indices to search are {} in the database {}".format(self._indices_array,self._source_type))
        return self._indices_array
