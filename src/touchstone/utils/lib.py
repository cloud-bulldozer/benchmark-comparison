import logging
import sys


_logger = logging.getLogger("touchstone")


def print_metadata_dict(uuid, d, output_file=sys.stdout, message=""):
    for k, v in d.items():
        if isinstance(v, dict):
            message = "{0}, ".format(k)
            print_metadata_dict(uuid, v, output_file, message)
        else:
            output_file.write("{0}, {1}{2}, {3}\n".format(uuid, message, k, v))


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


def print_csv(header, data, buckets, output_file):
    row_list = [header]

    def recurse(t, parent_key=""):
        if isinstance(t, dict):
            for k, v in t.items():
                if k in buckets:
                    recurse(v, str(parent_key))
                else:
                    recurse(v, str(parent_key) + ", " + str(k) if parent_key else k)
        else:
            row_list.append(parent_key + ", " + str(t))

    for metric in data:
        recurse(data[metric])
    for row in row_list:
        print(row, file=output_file)
