# -*- coding: utf-8 -*-
import argparse
import sys
import logging
import json

from touchstone import __version__
from . import benchmarks
from . import databases
from .utils.temp import compare_dict, dfs_dict_list, mergedicts

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
        choices=['uperf'],
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
        '-u', '--uuid',
        dest="uuid",
        help="2 uuids to compare",
        type=str,
        nargs='+')
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
    _logger.debug("Instantiating the benchmark instance")
    benchmark_instance = benchmarks.grab(args.benchmark,
                                         source_type=args.database,
                                         harness_type=args.harness)
    if len(args.conn_url) < len(args.uuid):
        args.conn_url = [args.conn_url[0]] * len(args.uuid)
    print("=" * 128)
    for index in benchmark_instance.emit_indices():
        _compare_header = "{:40} |".format("key")
        compare_uuid_dict = {}
        for key in benchmark_instance.emit_compare_map()[index]:
            compare_uuid_dict[key] = {}
        for uuid_index, uuid in enumerate(args.uuid):
            _compare_header += " {:40} |".format(uuid)
            database_instance = databases.grab(args.database,
                                               conn_url=args.conn_url[uuid_index])
            compare_uuid_dict = database_instance.emit_compare_dict(uuid=uuid,
                                                                    compare_map=benchmark_instance.emit_compare_map(),
                                                                    index=index,
                                                                    input_dict=compare_uuid_dict) # noqa
        print("------Key Metadata ---------- for index {}".format(index))
        for key in benchmark_instance.emit_compare_map()[index]:
            _message = "{:40} |".format(key)
            for uuid in args.uuid:
                _message += " {:40} |".format(compare_uuid_dict[key][uuid])
            print(_message)
        print("------Bucket aggregations---- for index {}".format(index))
        for compute in benchmark_instance.emit_compute_map()[index]:
            compute_uuid_dict = {}
            compute_aggs_set = []
            _compute_header = "{:30} |".format("bucket_name")
            _compute_value = "{:30} |".format("bucket_value")
            for key, value in compute['filter'].items():
                _compute_header += " {:20} |".format(key)
                _compute_value += " {:20} |".format(value)
            for uuid_index, uuid in enumerate(args.uuid):
                database_instance = databases.grab(args.database,
                                                   conn_url=args.conn_url[uuid_index])
                _current_uuid_dict = database_instance.emit_compute_dict(uuid=uuid,
                                                                        compute_map=compute,
                                                                        index=index,
                                                                        input_dict=compare_uuid_dict) # noqa
                compute_aggs_set = compute_aggs_set + database_instance._aggs_list
                compute_uuid_dict = dict(mergedicts(compute_uuid_dict, _current_uuid_dict))
            compute_aggs_set = set(compute_aggs_set)
            compute_buckets = database_instance._bucket_list
            # print(json.dumps(compute_uuid_dict,indent=4))
            compare_dict(compute_uuid_dict, compute_aggs_set, _compute_value, compute_buckets, args.uuid, _compute_header, max_level=2*len(compute_buckets))

    _logger.info("Script ends here")


def render():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    render()
