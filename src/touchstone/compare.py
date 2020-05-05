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
from .databases import prometheus

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
        choices=['uperf', 'ycsb', 'pgbench', 'vegeta', 'mb'],
        metavar="benchmark")
    parser.add_argument(
        dest="database",
        help="the type of database data is stored in",
        type=str,
        choices=['elasticsearch', 'prometheus'],
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
        '-input-file',
        dest="input_file",
        help="Input config file for metadata",
        type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument(
        '-output-file',
        dest="output_file",
        help="Redirect output of json/csv/yaml to file",
        type=argparse.FileType('w'))
    parser.add_argument(
        '-url', '--connection-url',
        dest="conn_url",
        help="the database connection strings in the same order as the uuids",
        type=str,
        nargs='+')
    parser.add_argument(
        '-name', '--metric_name',
        dest="metric_name",
        help="the name of the prometheus query metric",
        type=str,
        nargs='+')
    parser.add_argument(
        '-start', '--start_time',
        dest="start_time",
        help="the start time for the query parameter",
        type=str,
        nargs='+')
    parser.add_argument(
        '-end', '--end_time',
        dest="end_time",
        help="the end time for the query parameter",
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


def update(dict1, dict2):
    copy = dict1.copy()
    for key in dict2:
        if key in dict1:
            copy[key].update(dict2[key])
        else:
            copy[key] = dict2[key]
    return copy


def main(args):
    """Main entry external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    print_csv = False


    if args.database == 'elasticsearch':
        csv_header_metadata = "uuid, where, field, value"
        metadata_json = dict()
        main_json = dict()
        compare_uuid_dict_metadata = dict()
        compare_header_footer = "{}{}".format(("=" * 89), ("=" * 89))
        compare_output = compare_header_footer
        _logger.debug("Instantiating the benchmark instance")
        benchmark_instance = benchmarks.grab(args.benchmark,
                                             source_type=args.database,
                                             harness_type=args.harness)
        if len(args.conn_url) < len(args.uuid):
            args.conn_url = [args.conn_url[0]] * len(args.uuid)
        if args.output == "csv":
            print_csv = True
            printed_header = False
            printed_csv_header = False
        if args.input_file:
            config_file_metadata = json.load(args.input_file)
        if args.output_file:
            output_file = args.output_file
        else:
            output_file = sys.stdout
        # Indices from metadata map
        for uuid_index, uuid in enumerate(args.uuid):
            super_header = "\n{} UUID: {} {}".format(("=" * 67), uuid, ("=" * 67))
            compare_uuid_dict_metadata[uuid] = {}
            # Create database connection instance
            database_instance = databases.grab(args.database,
                                               conn_url=args.conn_url[uuid_index])
            # Set metadata search map based on existence of config file
            if args.input_file:
                metadata_search_map = config_file_metadata["metadata"]
            else:
                metadata_search_map = benchmark_instance.emit_metadata_search_map()
            index_dict = {}
            for index in metadata_search_map.keys():
                tmp_dict = {}
                # Adding emit_compare_metadata_dict to elasticsearch class
                database_instance.emit_compare_metadata_dict(uuid=uuid,
                                                             compare_map=metadata_search_map[
                                                                 index],
                                                             index=index,
                                                             input_dict=tmp_dict)  # noqa
                compare_uuid_dict_metadata[uuid] = tmp_dict
                index_dict = update(tmp_dict, index_dict)
            stockpile_metadata = {}
            stockpile_metadata["where"] = []
            for where in index_dict.keys():
                # Skip if there is no associated metadata
                if not index_dict[where].items():
                    continue
                stockpile_metadata["where"].append(where)
                for k, v in index_dict[where].items():
                    if k not in stockpile_metadata:
                        stockpile_metadata[k] = []
                    stockpile_metadata[k].append(v)
            # Check that metadata exists to be printed
            if stockpile_metadata["where"]:
                if args.output not in ["json", "yaml", "csv"]:
                    print(super_header)
                    print(tabulate(stockpile_metadata,
                                   headers="keys", tablefmt="pretty"))
                elif args.output in ["csv"]:
                    # Print to output file if argument present
                    if not printed_csv_header:
                        output_file.write(csv_header_metadata + "\n")
                        printed_csv_header = True
                    print_metadata_dict(uuid, compare_uuid_dict_metadata[uuid],
                                        output_file)
                elif args.output in ["json", "yaml"]:
                    metadata_json = dict(mergedicts(
                        metadata_json,
                        compare_uuid_dict_metadata))

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
                                                        compare_map=benchmark_instance.emit_compare_map(),
                                                        # noqa
                                                        index=index,
                                                        input_dict=compare_uuid_dict,  # noqa
                                                        identifier=args.identifier)
            compute_uuid_dict = {}
            for compute in benchmark_instance.emit_compute_map()[index]:
                current_compute_dict = {}
                compute_aggs_set = []
                for uuid_index, uuid in enumerate(args.uuid):
                    # Create database connection instance
                    database_instance = \
                        databases.grab(args.database,
                                       conn_url=args.conn_url[uuid_index])
                    # Add method emit_compute_dict to the elasticsearch class
                    catch = \
                        database_instance.emit_compute_dict(uuid=uuid,
                                                            compute_map=compute,  # noqa
                                                            index=index,
                                                            input_dict=compute_uuid_dict,  # noqa
                                                            identifier=args.identifier)  # noqa
                    if catch != {}:
                        current_compute_dict = \
                            dfs_list_dict(list(compute['filter'].items()),
                                          compute_uuid_dict,
                                          len(compute['filter']), catch)
                        compute_uuid_dict = \
                            dict(mergedicts(compute_uuid_dict, current_compute_dict))  # noqa
                        compute_aggs_set = \
                            compute_aggs_set + database_instance._aggs_list
                        compute_uuid_dict = \
                            dict(mergedicts(compute_uuid_dict, catch))
                compute_aggs_set = set(compute_aggs_set)
                compute_buckets = database_instance._bucket_list
            if args.output in ["json", "yaml"]:
                main_json = dict(mergedicts(main_json, compute_uuid_dict))
            else:
                # Stdout
                for key in benchmark_instance.emit_compare_map()[index]:
                    _message = "{:50} |".format(key)
                    for uuid in args.uuid:
                        _message += \
                            " {0:<60} |".format(compare_uuid_dict[key][uuid])
                    compare_output += "\n{}".format(_message)
                for compute in benchmark_instance.emit_compute_map()[index]:
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
                    # If csv, gather values from buckets in compute map
                    if print_csv:
                        for key in compute_buckets:
                            _compute_header += "{}, ".format(key)
                        _compute_header += "key, {}, value".format(args.identifier)
                        if not printed_header:
                            output_file.write(_compute_header + "\n")
                            printed_header = True
                    compare_dict(compute_uuid_dict, args.identifier,
                                 compute_aggs_set, _compute_value,
                                 compute_buckets, args.uuid, _compute_header,
                                 max_level=2 * len(compute_buckets),
                                 output_file=output_file, csv=print_csv)
        if args.output == "json":
            if metadata_json:
                output_file.write(json.dumps(metadata_json, indent=4))
            output_file.write(json.dumps(main_json, indent=4))
        elif args.output == "yaml":
            if metadata_json:
                output_file.write(yaml.dump(metadata_json, allow_unicode=True))
            output_file.write(yaml.dump(main_json, allow_unicode=True))
        elif args.output == "csv":
            pass
        else:
            compare_output += "\n" + compare_header_footer
            print(compare_output)

    elif args.database == 'prometheus':
        # Configurations are retrieved from the entered config yaml file in CLI argument.
        output = []

        if args.prom_config is not None:
            file_path = args.prom_config
            file = open(file_path)
            config = yaml.load(file, Loader=yaml.FullLoader)

            for i in range(len(config)):
                url = config[i]['url']
                query_list = config[i]['query_list']
                bearer_token = config[i]['bearer_token']
                disable_ssl = config[i]['disable_ssl']
                start_time_list = config[i]['start_time_list']
                end_time_list = config[i]['end_time_list']

                if bearer_token is not None:
                    headers = {"Authorization": "bearer " + bearer_token}
                else:
                    headers = None

                prometheus_object = databases.grab(args.database, query_list=query_list,
                                                   start_time_list=start_time_list,
                                                   url=url, end_time_list=end_time_list,
                                                   headers=headers,
                                                   disable_ssl=disable_ssl)
                output.extend(prometheus_object.compare_data())

        print(output)

    _logger.info("Script ends here")


def render():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    render()
