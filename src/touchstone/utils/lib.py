import logging


_logger = logging.getLogger("touchstone")


def print_metadata_dict(uuid, d, message=""):
    for k, v in d.items():
        if isinstance(v, dict):
            message = ("{0}, ".format(k))
            print_metadata_dict(uuid, v, message)
        else:
            print("{0}, {1}{2}, {3}".format(uuid, message, k, v))


def get(d, keys):
    if "." in keys:
        key, rest = keys.split(".", 1)
        return get(d[key], rest)
    else:
        return d[keys]


def id_dict(obj):
    return obj.__class__.__name__ == 'dict'


def snake(input_str):
    return input_str.replace('.', '_')


def dfs_list_dict(input_list, input_dict, max_level, end_value,
                  recurse_level=0):
    # This function helps with building a dictionary in dfs
    _recurse_level = recurse_level + 1
    if _recurse_level <= max_level:
        key, value = input_list[recurse_level]
        if key not in input_dict:
            input_dict[key] = {}
        if value not in input_dict[key]:
            input_dict[key][value] = {}
        input_dict[key][value] = \
            dict(mergedicts(dfs_list_dict(input_list, {}, max_level, end_value, _recurse_level), input_dict[key][value])) # noqa
        return input_dict
    else:
        return end_value


def dfs_dict_list(input_list, input_dict, max_level, recurse_level=0):
    _recurse_level = recurse_level + 1
    if _recurse_level <= max_level:
        for key, value in input_list[recurse_level].items():
            _output_dict = {}
            _output_dict[key] = {}
            _output_dict[key][value] = {}
            _output_dict[key][value] = \
                dfs_dict_list(input_list, {}, max_level, _recurse_level)
            return _output_dict
    else:
        return {}


def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict,
                # you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception
                # raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def compare_dict(d1, identifier, aggs, _message, buckets,
                 uuids, _header, max_level, csv=False, level=0):
    for key in d1:
        if type(d1[key]) is dict and key not in aggs and level < max_level - 1:
            new_level = level + 1
            if key not in buckets:
                # this means it's a bucket value
                if not csv:
                    new_message = _message + " {:60} |".format(key)
                else:
                    new_message = _message + "{}, ".format(key)
                compare_dict(d1[key], identifier, aggs, new_message, buckets,
                             uuids, _header, max_level, csv, new_level)
            else:
                # this means it's a bucket name
                if not csv:
                    new_header = _header + " {:60} |".format(key)
                else:
                    new_header = _header + "{}, ".format(key)
                compare_dict(d1[key], identifier, aggs, _message, buckets,
                             uuids, new_header, max_level, csv, new_level)
        else:
            bool_header = True
            if not csv:
                _output = _header + '\n'
                final_message = _message + " {:60} |".format(key)
                _output = _output + final_message + '\n'
                _compare_header = "{:50} |".format(identifier)
                for uuid in uuids:
                    _compare_header = \
                        _compare_header + " {:60} |".format(uuid[:16])
                _output = _output + _compare_header
                for agg_key, agg_dict in d1[key].items():
                    if len(agg_dict) < 2:
                        pass
                    else:
                        if bool_header:
                            print("=" * 178)
                            print(_output)
                            bool_header = False
                        _compare_values = "{:50} |".format(agg_key)
                        for uuid in uuids:
                            if uuid in agg_dict:
                                _compare_values = \
                                    _compare_values + " {:60} |".format(str(agg_dict[uuid])) # noqa
                            else:
                                _compare_values = \
                                    _compare_values + \
                                    " {:60} |".format("no_match")
                        print(_compare_values)
            else:
                _output = _message + "{}, ".format(key)
                for agg_key, agg_dict in d1[key].items():
                    output = _output + "{}, ".format(agg_key)
                    for uuid in uuids:
                        if uuid in agg_dict:
                            message = \
                                output + "{}, {}".format(uuid, str(agg_dict[uuid])) # noqa
                            print(message)
