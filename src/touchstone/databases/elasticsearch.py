import logging
import elasticsearch
import json
import copy
import queue
from elasticsearch_dsl import Search


from . import DatabaseBaseClass


_logger = logging.getLogger("touchstone")

class Elasticsearch(DatabaseBaseClass):

    def _create_conn_object(self):
        _logger.debug("Creating connection object")
        es = elasticsearch.Elasticsearch([str(self._conn_url)],send_get_body_as='POST')
        return es

    def __init__(self, conn_url=None):
        _logger.debug("Initializing Elasticsearch object")
        DatabaseBaseClass.__init__(self, conn_url=conn_url)
        self._conn_object = self._create_conn_object()
        self._possible_bucket_keys = {}
        _logger.debug("Finished Initializing Elasticsearch object")

    def _clean_dict(self, _input_dict, _list_buckets, level, aggs):
        _curr_level = level+1
        _output_dict = {}
        if _curr_level <= len(_list_buckets):
            _output_dict[_list_buckets[level]] = {}
            for _bucket in _input_dict[_list_buckets[level]]['buckets']:
                _real_key = _bucket['key']
                _output_dict[_list_buckets[level]][_real_key] = {}
                _output_dict[_list_buckets[level]][_real_key] = self._clean_dict(_bucket, _list_buckets, _curr_level, aggs)
        else:
            _key = _input_dict['key']
            _output_dict = {}
            for _aggs in aggs:
                if 'values' in _input_dict[_aggs]:
                    _output_dict[_aggs] = _input_dict[_aggs]['values']
                else:
                    _output_dict[_aggs] = _input_dict[_aggs]['value']
        return _output_dict


    def _build_dict(self, search_map, index, uuid):
        _temp_dict = {}
        buckets = search_map['buckets']
        self._bucket_list = []
        aggregations = search_map['aggregations']
        self._aggs_list = []
        _logger.debug("Initializing search object")
        s = Search(using=self._conn_object, index=str(index)).query("match", uuid=str(uuid))
        _logger.debug("Building query")
        _first_bucket = str(buckets[0].split('.')[0])
        self._bucket_list.append(_first_bucket)
        x=s.aggs.bucket(_first_bucket,'terms',field=str(buckets[0]))
        # _temp_dict[buckets[0].split('.')[0]] = {}
        # _temp_dict[buckets[0].split('.')[0]]['buckets'] = {}
        # y = _temp_dict[buckets[0].split('.')[0]]['buckets']
        _logger.debug("Building buckets")
        for bucket_name in buckets[1:]:
            _curr_bucket = bucket_name.split('.')[0]
            self._bucket_list.append(_curr_bucket)
            x=x.bucket(_curr_bucket,'terms',field=bucket_name)
            # y[bucket_name.split('.')[0]] = {}
            # y[bucket_name.split('.')[0]]['buckets'] = {}
            # y = y
        _logger.debug("Finished adding buckets to query")
        _logger.debug("Adding aggregations to query")
        for agg in aggregations:
            _temp_perc_str = str(agg) + str('_percentiles')
            self._aggs_list.append(_temp_perc_str)
            _temp_avg_str = str(agg) + str('_average')
            self._aggs_list.append(_temp_avg_str)
            x=x.metric(_temp_perc_str,'percentiles',field=agg,percents=[1,5,50,95,99])
            x=x.metric(_temp_avg_str,'avg',field=agg)
        _logger.debug("Finished adding aggregations to query")
        _logger.debug("Built the following query: {}".format(json.dumps(s.to_dict(), indent=4)))
        response = s.execute()
        _logger.debug("Succesfully executed the search query")
        _temp_dict_throw = response.aggregations.__dict__['_d_']
        _temp_dict = copy.deepcopy(_temp_dict_throw)
        _output_dict = self._clean_dict( _temp_dict, self._bucket_list, 0 ,self._aggs_list)
        if len(response.hits.hits) > 0:
            for compare in search_map['compare']:
                _output_dict[compare] = str(response.hits.hits[0]['_source'][compare])
        print("\n")
        print(_output_dict)
        print("\n")
        # _first_level = _queue_buckets.get()
        # _temp_dict[_first_level] = {}
        # _y = [_temp_dict]
        # _curr_object = response.aggregations[_first_level]
        # while 'buckets' in _curr_bucket:
        #     if not _queue_buckets.empty():
        #         _curr_level = _queue_buckets.get()
        #     else:
        #         _curr_level = None
        #     for _bucket in _curr_bucket['buckets']:
        #         _curr_level = _queue_buckets.get()
        #         for __y in _y:
        #             _temp_list = []
        #             _y[__y][_bucket['key']] = {}
        #             if _curr_level:
        #                 _y[__y][_bucket['key']][_curr_level] = {}
        #                 _temp_list.append(_y[__y][_bucket['key']][_curr_level])
        #             else:
        #                 # This means that we're down to the case of metrics
        #                 _y[__y][_bucket['key']] = {}
        #                 for _metric in self._aggs_list:
        #                     _y[__y][_bucket['key']][_metric] =
        #         _y = _temp_list
        return _output_dict

    def emit_values_dict(self, uuid=None, search_map=None):
        for index in search_map.keys():
            self._possible_bucket_keys[index] =  self._build_dict(search_map[index],index,uuid)
        return self._possible_bucket_keys
