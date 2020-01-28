import logging


_logger = logging.getLogger("touchstone")


def get(d, keys):
    if "." in keys:
        key, rest = keys.split(".", 1)
        return get(d[key], rest)
    else:
        return d[keys]

def id_dict(obj):
    return obj.__class__.__name__ == 'dict'

def snake(input_str):
    return input_str.replace('.','_')

def dfs_dict_list(input_list, input_dict, max_level, recurse_level=0):
    _recurse_level = recurse_level + 1
    if _recurse_level <= max_level:
        for key, value in input_list[recurse_level].items():
            _output_dict = {}
            _output_dict[key] = {}
            _output_dict[key][value] = {}
            _output_dict[key][value] = dfs_dict_list(input_list, {}, max_level, _recurse_level)
            return _output_dict
    else:
        return {}


def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def compare_dict(d1, aggs, _message, buckets, uuids, _header, max_level, level=0):
    for key in d1:
        if type(d1[key]) is dict and key not in aggs and level < max_level-1:
            new_level = level + 1
            if key not in buckets:
                # this means it's a bucket value
                new_message = _message + " {:20} |".format(key)
                compare_dict(d1[key], aggs, new_message, buckets,
                             uuids, _header, max_level, new_level)
            else:
                # this means it's a bucket name
                new_header = _header + " {:20} |".format(key)
                compare_dict(d1[key], aggs, _message, buckets,
                             uuids, new_header, max_level, new_level)
        else:
            bool_header = True
            _output = _header +'\n'
            #print(_header)
            final_message = _message + " {:20} |".format(key)
            _output = _output + final_message + '\n'
            # print(final_message)
            #print(_output)
            _compare_header = "{:30} |".format("key")
            for uuid in uuids:
                _compare_header = _compare_header + " {:20} |".format(uuid[:16])
            _output = _output + _compare_header
            # print(_compare_header)
            #print(_output)
            for agg_key, agg_dict in d1[key].items():
                if len(agg_dict) < 2:
                    #print("fewer than 2 uuids have the aggregations")
                    pass
                else:
                    if bool_header:
                        print("=" * 128)
                        print(_output)
                        bool_header = False
                    _compare_values = "{:40} |".format(agg_key)
                    for uuid in uuids:
                        if uuid in agg_dict:
                            _compare_values = _compare_values + " {:40} |".format(str(agg_dict[uuid]))
                        else:
                            _compare_values = _compare_values + " {:40} |".format("no_match")
                    print(_compare_values)
