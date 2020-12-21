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


def flatten_and_discard(data, headers, row_list=[], row=[]):
    if isinstance(data, dict):
        for k in data:
            new_row = copy.deepcopy(row)
            if k not in headers:
                new_row.append(k)
            flatten_and_discard(data[k], headers, row_list, new_row)
    else:
        row.append(data)
        row_list.append(row)
