import logging
import elasticsearch
import elasticsearch_dsl
import json
import copy
from elasticsearch_dsl import Search


from . import DatabaseBaseClass
from ..utils.lib import get


_logger = logging.getLogger("touchstone")


class Elasticsearch(DatabaseBaseClass):

    def _create_conn_object(self):
        _logger.debug("Creating connection object")
        es = elasticsearch.Elasticsearch([str(self._conn_url)],
                                         send_get_body_as='POST')
        return es

    def __init__(self, conn_url=None):
        _logger.debug("Initializing Elasticsearch object")
        DatabaseBaseClass.__init__(self, conn_url=conn_url)
        self._conn_object = self._create_conn_object()
        self._possible_bucket_keys = {}
        self._bucket_list = []
        self._aggs_list = []
        _logger.debug("Finished Initializing Elasticsearch object")

    def _clean_dict(self, _input_dict, _list_buckets, level, aggs, uuid,
                    _first_hit, _collate_list):
        _curr_level = level + 1
        _output_dict = {}
        if _curr_level <= len(_list_buckets):
            _output_dict[_list_buckets[level]] = {}
            for _bucket in _input_dict[_list_buckets[level]]['buckets']:
                _real_key = _bucket['key']
                _output_dict[_list_buckets[level]][_real_key] = {}
                _output_dict[_list_buckets[level]][_real_key] = \
                    self._clean_dict(_bucket, _list_buckets, _curr_level, aggs,
                                     uuid, _first_hit, _collate_list)
        else:
            # this is the last level
            _output_dict = {}
            for _aggs in aggs:
                if 'values' in _input_dict[_aggs]:
                    # where values is a dictionary
                    self._remove_aggs.append(_aggs)
                    for value in _input_dict[_aggs]['values'].keys():
                        _agg_str = value + str(_aggs)
                        self._aggs_list.append(_agg_str)
                        _output_dict[_agg_str] = {}
                        _output_dict[_agg_str][uuid] = \
                            _input_dict[_aggs]['values'][value]
                else:
                    _output_dict[_aggs] = {}
                    _output_dict[_aggs][uuid] = _input_dict[_aggs]['value']
            # Now do the lowest level compare
            for _collate_key in _collate_list:
                _output_dict[str(_collate_key)] = {}
                try:
                    _output_dict[str(_collate_key)][uuid] = \
                        get(_first_hit, _collate_key)
                except BaseException:  # replace with keynotfoundexception
                    _logger.debug("key not exists" + str(_collate_key))
                    pass
        return _output_dict

    def _build_values_dict(self, search_map, index, uuid, input_dict,
                           identifier):
        _temp_dict = {}
        buckets = search_map['buckets']
        aggregations = search_map['aggregations']
        collate = search_map['collate']
        filters = search_map['filter']
        _logger.debug("Initializing search object")
        _identifier = identifier + ".keyword"  # append .keyword
        s = Search(using=self._conn_object,
                   index=str(index)).query("match", **{str(_identifier):
                                                       str(uuid)})
        for key, value in filters.items():
            s = s.filter("term", **{str(key): str(value)})
        if 'exclude' in search_map:
            for key, value in search_map['exclude'].items():
                s = s.exclude('match', **{key: value})
        _logger.debug("Building query")
        _first_bucket = str(buckets[0].split('.')[0])
        self._bucket_list.append(_first_bucket)
        x = s.aggs.bucket(_first_bucket, 'terms', field=str(buckets[0]))
        _logger.debug("Building buckets")
        for bucket_name in buckets[1:]:
            _curr_bucket = bucket_name.split('.')[0]
            self._bucket_list.append(_curr_bucket)
            x = x.bucket(_curr_bucket, 'terms', field=bucket_name)
        _logger.debug("Finished adding buckets to query")
        _logger.debug("Adding aggregations to query")
        for key, agg_list in aggregations.items():
            for aggs in agg_list:
                if isinstance(aggs, str):
                    _temp_agg_str = "{}({})".format(aggs, key)
                    x = x.metric(_temp_agg_str, aggs, field=key)
                    self._aggs_list.append(_temp_agg_str)
                elif isinstance(aggs, dict):
                    for dict_key, dict_value in aggs.items():
                        _temp_agg_str = "{}({})".format(dict_key, key)
                        for nested_dict_key, nested_dict_value in dict_value.items(): # noqa
                            x = x.metric(_temp_agg_str, dict_key, field=key,
                                         **{nested_dict_key: nested_dict_value}) # noqa
                        self._aggs_list.append(_temp_agg_str)
        _logger.debug("Finished adding aggregations to query")
        _logger.debug("Built the following query: \
                        {}".format(json.dumps(s.to_dict(), indent=4)))
        response = s.execute()
        _logger.debug("Succesfully executed the search query")
        _temp_dict_throw = response.aggregations.__dict__['_d_']
        _temp_dict = copy.deepcopy(_temp_dict_throw)
        self._remove_aggs = []
        if len(response.hits.hits) == 0:
            return {}
        _output_dict = self._clean_dict(_temp_dict, self._bucket_list,
                                        0, copy.deepcopy(self._aggs_list),
                                        uuid,
                                        response.hits.hits[0].__dict__['_d_']['_source'], # noqa
                                        collate)
        self._remove_aggs = set(self._remove_aggs)
        for element in self._remove_aggs:
            self._aggs_list.remove(element)
        _logger.debug("output compute dictionary with summaries is: {}\
                        ".format(json.dumps(_output_dict, indent=4)))
        return _output_dict

    def _build_compare_dict(self, compare_map, index, uuid, input_dict,
                            identifier):
        _logger.debug("Initializing search object")
        _identifier = identifier + ".keyword"  # append .keyword
        s = Search(using=self._conn_object,
                   index=str(index)).query("match", **{str(_identifier):
                                                       str(uuid)})
        response = s.execute()
        if len(response.hits.hits) > 0:
            for compare_key in compare_map:
                temp_value = get(response.hits.hits[0]['_source'],
                                 str(compare_key))
                if isinstance(temp_value, elasticsearch_dsl.utils.AttrList):
                    input_dict[compare_key][uuid] = temp_value[0]
                else:
                    input_dict[compare_key][uuid] = temp_value
        _logger.debug("output compare dictionary with summaries is: {}\
                        ".format(json.dumps(input_dict, indent=4)))
        return input_dict

    def emit_compute_dict(self, uuid=None, compute_map=None, index=None,
                          input_dict=None, identifier=None):
        return self._build_values_dict(compute_map, index, uuid, input_dict,
                                       identifier)

    def emit_compare_dict(self, uuid=None, compare_map=None, index=None,
                          input_dict=None, identifier=None):
        return self._build_compare_dict(compare_map[index], index, uuid,
                                        input_dict, identifier)

    def emit_compare_metadata_dict(self, uuid=None, compare_map=None,
                                   index=None, input_dict=None):
        _logger.debug("Initializing metadata search object")
        s = Search(using=self._conn_object,
                   index=index).query("match", **{"uuid.keyword": uuid})
        response = s.execute()
        for hit in response.hits.hits:
            compare_by = self.access_nested_field(hit['_source'],
                                                  compare_map["element"])
            if compare_by not in input_dict:
                input_dict[compare_by] = {}
            for compare in compare_map["compare"]:
                value = self.access_nested_field(hit['_source'], compare)
                if value:
                    input_dict[compare_by][compare] = \
                        hit['_source']["value"][compare] = value
        return input_dict

    def access_nested_field(self, d, fields):
        tmp_dict = d
        for field in fields.split("."):
            if field in tmp_dict:
                tmp_dict = tmp_dict[field]
            else:
                return None
        return tmp_dict
