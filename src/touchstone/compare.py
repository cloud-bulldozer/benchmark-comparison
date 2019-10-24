# -*- coding: utf-8 -*-
import argparse
import sys
import logging

from touchstone import __version__
from . import benchmarks
from . import databases
from .utils.temp import compare_dict

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
        nargs=2)
    parser.add_argument(
        '-url', '--connection-url',
        dest="conn_url",
        help="the database connection strings in the same order as the uuids",
        type=str,
        nargs=2)
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
    benchmark_instance = benchmarks.grab(args.benchmark,source_type=args.database,harness_type=args.harness)
    print(benchmark_instance.emit_search_map())
    database_instance1 = databases.grab(args.database,conn_url=args.conn_url[0])
    database_instance2 = databases.grab(args.database,conn_url=args.conn_url[1])
    d1 = database_instance1.emit_values_dict(uuid=args.uuid[0],search_map=benchmark_instance.emit_search_map())
    d2 = database_instance2.emit_values_dict(uuid=args.uuid[1],search_map=benchmark_instance.emit_search_map())
    _logger.info("Script ends here")
    _header = ""
    for _bucket in database_instance1._bucket_list:
        _header = _header + " {:20} |".format(_bucket)
    print(_header)
    print("================================================================================================================================")
    # d1 = {'a': {'b': {'cs': 10}, 'd': {'cs': 20}}}
    # d2 = {'a': {'b': {'cs': 30}, 'd': {'cs': 20}}, 'newa': {'q': {'cs': 50}}}
    compare_dict(d1,d2,database_instance1._aggs_list,"",database_instance1._bucket_list)


def render():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    render()
