import logging
import elasticsearch
import json
from elasticsearch_dsl import Search, A

from . import DatabaseBaseClass


logger = logging.getLogger("touchstone")


class Elasticsearch(DatabaseBaseClass):
    def _create_conn_object(self):
        logger.debug("Creating connection object")
        es = elasticsearch.Elasticsearch([self._conn_url], send_get_body_as="POST")
        return es

    def __init__(self, conn_url=None):
        logger.debug("Initializing Elasticsearch object")
        DatabaseBaseClass.__init__(self, conn_url=conn_url)
        self._conn_object = self._create_conn_object()
        self._aggs_list = []
        logger.debug("Finished Initializing Elasticsearch object")

    def gen_result_dict(self, reponse, buckets, aggs, uuid):
        output_dict = {}
        input_dict = reponse.aggs.__dict__
        # Remove .keyword from bucket names
        buckets = [e.split(".keyword")[0] for e in buckets]

        def build_dict(input_dict, output_dict):
            # Iterate through buckets and check if that bucket exists in input_dict
            for b in buckets:
                # If the bucket exists, add it
                if b in input_dict:
                    output_dict[b] = {}
                    # Iterate through bucket values and recurse with each nested bucket
                    for bucket in input_dict[b]["buckets"]:
                        output_dict[b][bucket["key"]] = {}
                        build_dict(bucket, output_dict[b][bucket["key"]])
            # This is supposed to run in the last level
            for agg in aggs:
                # If the aggregation name is in this level and a value is found for that aggregation,
                # we add it to the output dict
                if agg in input_dict and "values" in input_dict[agg]:
                    for name, value in input_dict[agg]["values"].items():
                        agg_name = "{}{}".format(name, agg)
                        output_dict[agg_name] = {}
                        output_dict[agg_name][uuid] = value
                elif agg in input_dict:
                    output_dict[agg] = {}
                    output_dict[agg][uuid] = input_dict[agg]["value"]

        build_dict(input_dict["_d_"], output_dict)
        return output_dict

    def emit_compute_dict(self, uuid, compute_map, index, identifier):
        """
        Returns the normalized data from the ES query
        """
        output_dict = {}
        if "buckets" and "aggregations" and "filter" not in compute_map:
            logger.critical(f"Incorrect JSON data: nested dictionaries buckets, aggregations and filter \
fields are required in {compute_map}")
            exit(1)
        buckets = compute_map["buckets"]
        aggregations = compute_map["aggregations"]
        filters = compute_map["filter"]

        logger.debug("Initializing search object")
        kw_identifier = identifier + ".keyword"  # append .keyword
        s = Search(using=self._conn_object, index=str(index)).query(
            "match", **{kw_identifier: uuid}
        )

        # Apply filters
        for key, value in filters.items():
            s = s.filter("term", **{key: value})

        # Apply excludes
        if "exclude" in compute_map:
            for exclude in compute_map["exclude"]:
                s = s.exclude("match", **exclude)

        logger.debug("Building buckets")
        a = A("terms", field=buckets[0], size=10000)
        x = s.aggs.bucket(buckets[0].split(".keyword")[0], a)
        for bucket in buckets[1:]:
            a = A("terms", field=bucket, size=10000)
            # Create bucket with and trimming characters after .
            x = x.bucket(bucket.split(".keyword")[0], a)
        logger.debug("Finished adding buckets to query")
        logger.debug("Adding aggregations to query")
        for key, agg_list in aggregations.items():
            for aggs in agg_list:
                if isinstance(aggs, str):
                    _temp_agg_str = "{}({})".format(aggs, key)
                    # Create aggregation based on the key
                    a.metric(_temp_agg_str, aggs, field=key)
                    self._aggs_list.append(_temp_agg_str)
                # If there's a dictionary of aggregations. i.e different percentiles
                # we have to iterate through keys and values
                elif isinstance(aggs, dict):
                    for dict_key, dict_value in aggs.items():
                        _temp_agg_str = "{}({})".format(dict_key, key)
                        # Add nested dict as aggregation
                        a.metric(_temp_agg_str, dict_key, field=key, **dict_value)
                        self._aggs_list.append(_temp_agg_str)
                else:
                    logger.warn("Ignoring aggregation {}".format(aggs))
        logger.debug("Finished adding aggregations to query")
        logger.debug(
            "Built the following query: {}".format(json.dumps(s.to_dict(), indent=4))
        )
        response = s.execute()
        logger.debug("Succesfully executed the search query")

        if len(response.hits.hits) == 0:
            return {}
        _output_dict = self.gen_result_dict(response, buckets, self._aggs_list, uuid)
        if filters:
            output_dict = _output_dict
            filter_list = []
            for key, value in filters.items():
                filter_list.append(key)
                filter_list.append(value)
            # Include all k,v from filters as keys in the output dictionary
            for key in reversed(filter_list):
                output_dict = {key.split(".keyword")[0]: output_dict}
        else:
            output_dict = _output_dict
        logger.debug(
            "output compute dictionary with summaries is: {}".format(
                json.dumps(output_dict, indent=4)
            )
        )
        return output_dict

    def emit_compare_metadata_dict(self, uuid=None, compare_map=None, index=None):
        logger.debug("Initializing metadata search object")
        metadata_dict = {}
        s = Search(using=self._conn_object, index=index).query("match", **{"uuid.keyword": uuid})
        response = s.execute()
        for hit in response.hits.hits:
            compare_by = None
            if "element" in compare_map and compare_map["element"] in hit["_source"]:
                compare_by = hit["_source"][compare_map["element"]]
                metadata_dict[compare_by] = {}
            for compare in compare_map["compare"]:
                value = self.access_nested_field(hit["_source"], compare)
                if value and compare_by:
                    metadata_dict[compare_by][compare] = value
                elif value:
                    metadata_dict["NA"] = {compare: value}
        return metadata_dict

    def access_nested_field(self, d, fields):
        tmp_dict = d
        for field in fields.split("."):
            if field in tmp_dict:
                tmp_dict = tmp_dict[field]
            else:
                return None
        return tmp_dict
