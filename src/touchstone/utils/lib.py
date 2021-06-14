import copy


def mergedicts(dict1, dict2, parent_dict={}, parent_key=""):
    if isinstance(dict1, dict):
        for k in dict1:
            if k in dict2:
                mergedicts(dict1[k], dict2[k], dict2, k)
            else:
                dict2[k] = {}
                mergedicts(dict1[k], dict2[k], dict2, k)
    # dict1 is a value, so we add it
    else:
        parent_dict[parent_key] = dict1


def flatten_and_discard(data, discard_keys=[], row_list=[]):
    """
    Flattens a dictionary and discards keys given by discard_keys
    :arg data: Input dicitionary to flatten
    :arg discard_keys: List of keys to discard
    :arg row_list: List to append the flattened dictionary
    """

    def inner_function(input_data, row=[]):
        if isinstance(input_data, dict):
            for k in input_data:
                new_row = copy.deepcopy(row)
                if k not in discard_keys:
                    new_row.append(k)
                inner_function(input_data[k], new_row)
        else:
            row.append(input_data)
            row_list.append(row)

    inner_function(data)


def extract_headers(compute_config, identifier):
    """
    Extracts the headers from a compute configuration
    :arg compute_config: Input compute configuration
    :arg identifier: Key identifier
    """
    compute_header = []
    for key in compute_config.get("filter", []):
        compute_header.append(key.split(".keyword")[0])
    for bucket in compute_config.get("buckets", []):
        compute_header.append(bucket.split(".keyword")[0])
    for extra_h in ["key", identifier, "value"]:
        compute_header.append(extra_h)
    return compute_header
