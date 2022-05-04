import argparse
import logging
import json
import yaml
import sys
import csv
from tabulate import tabulate

from touchstone import __version__
from touchstone.benchmarks.generic import Benchmark
from touchstone import decision_maker
from . import databases
from .utils.lib import mergedicts, flatten_and_discard, extract_headers

__author__ = "red-hat-perfscale"
__copyright__ = "red-hat-perfscale"
__license__ = "Apache License 2.0"

logger = logging.getLogger("touchstone")


def parse_args(args):
    """Parse command line parameters
    Args:
      args ([str]): command line parameters as list of strings
    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="compare results from benchmarks")
    parser.add_argument(
        "--version",
        action="version",
        version="touchstone {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "--database",
        default="elasticsearch",
        help="the type of database data is stored in",
        type=str,
        choices=["elasticsearch"],
    )
    parser.add_argument(
        "--identifier-key",
        dest="identifier",
        help="identifier key name(default: uuid)",
        type=str,
        default="uuid",
    )
    parser.add_argument(
        "-u",
        "--uuid",
        required=True,
        help="identifier values to fetch results and compare",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-a",
        "--aliases",
        help="id aliases",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="How should touchstone output the result",
        type=str,
        choices=["json", "yaml", "csv"],
    )
    parser.add_argument(
        "--config",
        help="Touchstone configuration file",
        required=True,
        type=argparse.FileType("r", encoding="utf-8"),
    )
    parser.add_argument(
        "--output-file",
        dest="output_file",
        help="Redirect output of json/csv/yaml to file",
        type=argparse.FileType("w"),
    )
    parser.add_argument(
        "--tolerancy-rules",
        help="Path to tolerancy rules configuration",
        type=argparse.FileType("r", encoding="utf-8"),
    )
    parser.add_argument(
        "--rc",
        help="Return code if tolerancy check fails",
        required=False,
        type=int,
        default=1,
    )
    parser.add_argument(
        "-url",
        "--connection-url",
        required=True,
        dest="conn_url",
        help="the database connection strings in the same order as the uuids",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging
    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.level = loglevel


def main(args):
    """Main entry point allowing external calls
    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    rc = 0
    if args.aliases and len(args.uuid) != len(args.aliases):
        logger.critical("Number of aliases must be equal to the number of IDs")
        sys.exit(1)
    setup_logging(args.loglevel)
    main_json = {}
    logger.debug("Instantiating the benchmark instance")
    benchmark_instance = Benchmark(args.config, args.database)
    if len(args.conn_url) < len(args.uuid):
        args.conn_url = [args.conn_url[0]] * len(args.uuid)
    output_file = args.output_file if args.output_file else sys.stdout
    # Get indices from metadata map
    metadata_search_map = benchmark_instance.search_map_metadata
    metadata_dict = {}
    if args.tolerancy_rules and (len(args.uuid) < 2 or len(args.uuid) > 2):
        logger.critical("Two uuids exactly are required when tolerancy-rules flag is passed")
        sys.exit(1)
    for index in metadata_search_map.keys():
        # Set metadata search map
        for uuid_index, uuid in enumerate(args.uuid):
            # Create database connection instance
            database_instance = databases.grab(args.database, conn_url=args.conn_url[uuid_index])
            # Adding emit_compare_metadata_dict to elasticsearch class
            database_instance.get_metadata(uuid, metadata_search_map[index], index, metadata_dict)
        headers = [metadata_search_map[index].get("additional_fields", []), "metadata"]
        if args.aliases:
            headers += args.aliases
        else:
            headers += args.uuid
        headers.append("value")
        if metadata_dict and not args.tolerancy_rules:
            if args.output == "csv":
                row_list = [headers]
                flatten_and_discard(metadata_dict, headers, row_list)
                writer = csv.writer(output_file, delimiter=",")
                list(map(writer.writerow, row_list))
                metadata_dict = {}
            elif not args.output:
                row_list = []
                flatten_and_discard(metadata_dict, headers, row_list)
                print(tabulate(row_list, headers=headers, tablefmt="pretty"), file=output_file)
                metadata_dict = {}

    timeseries_result = 0
    # Iterate through indexes
    for index in benchmark_instance.get_indices():
        for compute in benchmark_instance.compute_map[index]:
            # index_json is used for csv and standard output. Since the header may be different in each index
            # we need to print csv or stdout for each index
            index_json = {}
            # Iterate through UUIDs
            for uuid_index, uuid in enumerate(args.uuid):
                # Create database connection instance
                database_instance = databases.grab(args.database, conn_url=args.conn_url[uuid_index])
                # Add method emit_compute_dict to the elasticsearch class
                if "aggregations" in compute:
                    alias = args.aliases[uuid_index] if args.aliases else None
                    result = database_instance.emit_compute_dict(
                        uuid=uuid,
                        compute_map=compute,
                        index=index,
                        identifier=args.identifier,
                        alias=alias,
                    )
                    if not result:
                        logger.error(
                            f"Error: Issue capturing results from {args.database} using config {compute}"
                        )
                    mergedicts(result, main_json)
                    mergedicts(result, index_json)
                    compute_header = extract_headers(compute, args.uuid, args.aliases)

                elif "timeseries" in compute and compute["timeseries"]:
                    timeseries_result = database_instance.get_timeseries_results(
                        uuid=uuid, compute_map=compute, index=index, identifier=args.identifier
                    )
                    if not timeseries_result:
                        logger.error(
                            f"Error: Issue capturing results from {args.database} using config {compute}"
                        )
                        return {}
                    mergedicts(timeseries_result, main_json)
                    mergedicts(timeseries_result, index_json)

                else:
                    logger.error("Not Supported configuration")
            if timeseries_result:
                if not args.output or args.output == "json":
                    output_file.write(json.dumps(timeseries_result, indent=4))
                if args.output == "yaml":
                    output_file.write(yaml.dump(timeseries_result, allow_unicode=True))
                return
            if index_json and not args.tolerancy_rules:
                row_list = []
                if args.output == "csv":
                    row_list.append(compute_header)
                    flatten_and_discard(index_json, compute_header, row_list)
                    writer = csv.writer(output_file, delimiter=",")
                    list(map(writer.writerow, row_list))
                elif not args.output:
                    flatten_and_discard(index_json, compute_header, row_list)
                    print(tabulate(row_list, headers=compute_header, tablefmt="pretty"), file=output_file)
            elif args.tolerancy_rules:
                baseline_uuid = args.aliases[0] if args.aliases else args.uuid[0]
                identifiers = args.aliases if args.aliases else args.uuid
                compute_header = extract_headers(compute) + ["result", "deviation"] + identifiers
                if decision_maker.run(baseline_uuid, index_json, compute_header, output_file, args):
                    rc = args.rc
    if metadata_dict:
        main_json["metadata"] = metadata_dict
    if args.output == "json":
        output_file.write(json.dumps(main_json, indent=4))
    elif args.output == "yaml":
        output_file.write(yaml.dump(main_json, allow_unicode=True))
    exit(rc)


def render():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    render()
