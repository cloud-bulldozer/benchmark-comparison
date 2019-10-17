from importlib import import_module
import logging

from . base_benchmark import BenchmarkBaseClass ## noqa


_logger = logging.getLogger("touchstone")

def grab(benchmark_input_type, *args, **kwargs):
    try:
        _logger.debug("Grabbing the right benchmark instance")
        if '.' in benchmark_input_type:
            module_name, class_name = benchmark_input_type.rsplit('.', 1)
        else:
            module_name = benchmark_input_type
            class_name = benchmark_input_type.capitalize()
        _logger.debug("Importing the right benchmark module")
        benchmark_module = import_module('touchstone.benchmarks.' + module_name,
                                      package='benchmarks')
        benchmark_input_class = getattr(benchmark_module, class_name)
        _logger.debug("Creating the benchmark instance")
        instance = benchmark_input_class(*args, **kwargs)

    except (AttributeError, ModuleNotFoundError):
        _logger.debug("Hit an error finding the right module")
        raise ImportError('{} is not part of our benchmark collection!'.format(benchmark_input_type))
    return instance
