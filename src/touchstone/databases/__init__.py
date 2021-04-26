from importlib import import_module
import logging
import traceback

from .base_database import DatabaseBaseClass  ## noqa


_logger = logging.getLogger("touchstone")


def grab(database_input_type, *args, **kwargs):

    try:
        if "." in database_input_type:
            module_name, class_name = database_input_type.rsplit(".", 1)
        else:
            module_name = database_input_type
            class_name = database_input_type.capitalize()
        database_module = import_module("touchstone.databases." + module_name, package="databases")
        database_input_class = getattr(database_module, class_name)
        instance = database_input_class(*args, **kwargs)

    except Exception:
        _logger.debug("Hit an error finding the right module")
        _logger.error(traceback.format_exc())
    return instance
