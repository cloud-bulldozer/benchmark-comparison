# -*- coding: utf-8 -*-
import argparse
import sys
import logging
import json
import yaml
from tabulate import tabulate

from touchstone import __version__
from . import benchmarks
from . import databases
from .utils.lib import print_metadata_dict, compare_dict, \
    mergedicts, dfs_list_dict

__author__ = "aakarshg"
__copyright__ = "aakarshg"
__license__ = "mit"

_logger = logging.getLogger("touchstone")


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="compare results from benchmarks")
    parser.add_argument(
        "--version",
        action="version",
        version="touchstone {ver}".format(ver=__version__))
    parser.add_argument(
        dest="benchmark",
        help="which type of benchmark to compare",
        type=str,
        choices=['uperf', 'ycsb', 'pgbench', 'vegeta'],
        metavar="benchmark")
    parser.add_argument(
        dest="database",
        help="the type of database data is stored in",
        type=str,
        choices=['elasticsearch'],
        metavar="database")
    parser.add_argument(
        dest="harness",
        help="the test harness that was used to run the benchmark",
        type=str,
        choices=['ripsaw'],
        metavar="harness")
    parser.add_argument(
        '-id', '--identifier-key',
        dest="identifier",
        help="identifier key name(default: uuid)",
        type=str,
        metavar="identifier",
        default="uuid")
    parser.add_argument(
        '-u', '--uuid',
        dest="uuid",
        help="identifier values to fetch results and compare",
        type=str,
        nargs='+')
    parser.add_argument(
        '-o', '--output',
        dest="output",
        help="How should touchstone output the result",
        type=str,
        choices=['json', 'yaml', 'csv'])
    parser.add_argument(
        '-url', '--connection-url',
        dest="conn_url",
        help="the database connection strings in the same order as the uuids",
        type=str,
        nargs='+')
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO)
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    print_csv = False
    main_json = dict()
    compare_uuid_dict_metadata = dict()
    metadata = "{} Key Metadata {}".format(("=" * 82), ("=" * 82))
    _logger.debug("Instantiating the benchmark instance")
    benchmark_instance = benchmarks.grab(args.benchmark,
                                         source_type=args.database,
                                         harness_type=args.harness)
    if len(args.conn_url) < len(args.uuid):
        args.conn_url = [args.conn_url[0]] * len(args.uuid)
    if args.output == "csv":
        print_csv = True
        printed_header = False

    # Indices from metadata map
    for uuid_index, uuid in enumerate(args.uuid):
        super_header = "\n{} UUID: {} {}".format(("=" * 65), uuid, ("=" * 65))
        compare_uuid_dict_metadata[uuid] = {}
        # Create database connection instance
        database_instance = databases.grab(args.database,
                                           conn_url=args.conn_url[uuid_index])
        for index in benchmark_instance.emit_metadata_search_map().keys():
            input_dict = {}
            # Adding emit_compare_metadata_dict to elasticsearch class
            database_instance.emit_compare_metadata_dict(uuid=uuid,
            compare_map=benchmark_instance.emit_metadata_search_map()[index],
                                                         index=index,
                                                         input_dict=input_dict)  # noqa
            compare_uuid_dict_metadata[uuid] = input_dict
            stockpile_metadata = {}
            stockpile_metadata["where"] = []
            for where in input_dict.keys():
                stockpile_metadata["where"].append(where)
                for k, v in input_dict[where].items():
                    if k not in stockpile_metadata:
                        stockpile_metadata[k] = []
                    stockpile_metadata[k].append(v)
            if args.output not in ["json", "yaml", "csv"]:
                print(super_header)
                print(tabulate(stockpile_metadata,
                               headers="keys", tablefmt="grid"))
            elif args.output in ["csv"]:
                print_metadata_dict(uuid, compare_uuid_dict_metadata)

    # Indices from entered harness (ex: ripsaw)
    for index in benchmark_instance.emit_indices():
        compare_uuid_dict = {}  # Dict to hold fields under 'compare' field
        for key in benchmark_instance.emit_compare_map()[index]:
            compare_uuid_dict[key] = {}
        for uuid_index, uuid in enumerate(args.uuid):
            # Create database connection instance
            database_instance = \
                databases.grab(args.database,
                               conn_url=args.conn_url[uuid_index])
            # Add method emit_compare_dict to the elasticsearch class
            compare_uuid_dict = \
                database_instance.emit_compare_dict(uuid=uuid,
                                                    compare_map=benchmark_instance.emit_compare_map(), # noqa
                                                    index=index,
                                                    input_dict=compare_uuid_dict, # noqa
                                                    identifier=args.identifier)
        if args.output in ["json", "yaml"]:
            compute_uuid_dict = {}  # Dict to hold fields under 'compute' field
            for compute in benchmark_instance.emit_compute_map()[index]:
                current_compute_dict = {}
                for uuid_index, uuid in enumerate(args.uuid):
                    # Create database connection instance
                    database_instance = \
                        databases.grab(args.database,
                                       conn_url=args.conn_url[uuid_index])
                    # Add method emit_compute_dict to the elasticsearch class
                    catch = \
                        database_instance.emit_compute_dict(uuid=uuid,
                                                            compute_map=compute, # noqa
                                                            index=index,
                                                            input_dict=compare_uuid_dict, # noqa
                                                            identifier=args.identifier) # noqa
                    if catch != {}:
                        current_compute_dict = \
                            dfs_list_dict(list(compute['filter'].items()),
                                          compute_uuid_dict,
                                          len(compute['filter']), catch)
                        compute_uuid_dict = \
                            dict(mergedicts(compute_uuid_dict, current_compute_dict)) # noqa
            main_json = dict(mergedicts(main_json, compute_uuid_dict))
        else:
            # Stdout
            for key in benchmark_instance.emit_compare_map()[index]:
                _message = "{:50} |".format(key)
                for uuid in args.uuid:
                    _message += " {:60} |".format(compare_uuid_dict[key][uuid])
                metadata += "\n{}".format(_message)
            for compute in benchmark_instance.emit_compute_map()[index]:
                compute_uuid_dict = {}
                compute_aggs_set = []
                # If not csv, format bucket header
                if not print_csv:
                    _compute_header = "{:50} |".format("bucket_name")
                    _compute_value = "{:50} |".format("bucket_value")
                else:
                    _compute_header = ""
                    _compute_value = ""
                # Format filter output with values in compute map
                for key, value in compute['filter'].items():
                    if not print_csv:
                        _compute_header += " {:20} |".format(key)
                        _compute_value += " {:20} |".format(value)
                    else:
                        _compute_header += "{}, ".format(key)
                        _compute_value += "{}, ".format(value)

                for uuid_index, uuid in enumerate(args.uuid):
                    # Repeats earlier code - needs cleanup
                    database_instance = \
                        databases.grab(args.database,
                                       conn_url=args.conn_url[uuid_index])
                    _current_uuid_dict = \
                        database_instance.emit_compute_dict(uuid=uuid,
                                                    compute_map=compute,
                                                    index=index,
                                                    input_dict=compare_uuid_dict, # noqa
                                                    identifier=args.identifier) # noqa
                    compute_aggs_set = \
                        compute_aggs_set + database_instance._aggs_list
                    compute_uuid_dict = \
                        dict(mergedicts(compute_uuid_dict, _current_uuid_dict))
                compute_aggs_set = set(compute_aggs_set)
                compute_buckets = database_instance._bucket_list
                # If csv, gather values from buckets in compute map
                if print_csv:
                    for key in compute_buckets:
                        _compute_header += "{}, ".format(key)
                    _compute_header += "key, {}, value".format(args.identifier)
                    if not printed_header:
                        print(_compute_header)
                        printed_header = True
                compare_dict(compute_uuid_dict, args.identifier,
                             compute_aggs_set, _compute_value,
                             compute_buckets, args.uuid, _compute_header,
                             max_level=2 * len(compute_buckets), csv=print_csv)
    if args.output == "json":
        print(json.dumps(compare_uuid_dict_metadata, indent=4))
        print(json.dumps(main_json, indent=4))
    elif args.output == "yaml":
        print(yaml.dump(compare_uuid_dict_metadata, allow_unicode=True))
        print(yaml.dump(main_json, allow_unicode=True))
    elif args.output == "csv":
        pass
    else:
        metadata += "\n{} End Metadata {}".format(("=" * 82), ("=" * 82))
        print(metadata)
    _logger.info("Script ends here")


def render():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    render()
