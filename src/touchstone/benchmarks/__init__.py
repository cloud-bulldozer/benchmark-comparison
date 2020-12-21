from importlib import import_module
import logging
import traceback

from .base_benchmark import BenchmarkBaseClass  ## noqa


logger = logging.getLogger("touchstone")


def grab(benchmark_input_type, *args, **kwargs):
    try:
        logger.debug("Grabbing the right benchmark instance")
        if "." in benchmark_input_type:
            mod_name, class_name = benchmark_input_type.rsplit(".", 1)
        else:
            mod_name = benchmark_input_type
            class_name = benchmark_input_type.capitalize()
        logger.debug("Importing the right benchmark module")
        benchmark_module = import_module(
            "touchstone.benchmarks." + mod_name, package="benchmarks"
        )
        benchmark_input_class = getattr(benchmark_module, class_name)
        logger.debug("Creating the benchmark instance")
        instance = benchmark_input_class(*args, **kwargs)

    except Exception:
        logger.debug("Hit an error finding the right module")
        logger.error(traceback.format_exc())
    return instance
