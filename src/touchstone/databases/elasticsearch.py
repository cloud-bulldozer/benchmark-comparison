from . import DatabaseBaseClass

class Elasticsearch(DatabaseBaseClass):

    def _build_keys(self):
        output_dict = {'database_name':'elasticsearch'}
        return output_dict

    def __init__(self):
        DatabaseBaseClass.__init__(self)
        self._dict = self._build_keys()

    def emit_values_dict(self):
        return self._dict
