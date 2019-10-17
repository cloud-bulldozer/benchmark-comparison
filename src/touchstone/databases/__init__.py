from importlib import import_module
import logging

from . base_database import DatabaseBaseClass ## noqa


_logger = logging.getLogger("touchstone")


def grab(database_input_type, *args, **kwargs):

    try:
        if '.' in database_input_type:
            module_name, class_name = database_input_type.rsplit('.', 1)
        else:
            module_name = database_input_type
            class_name = database_input_type.capitalize()
        database_module = import_module('touchstone.databases.' + module_name,
                                      package='databases')
        database_input_class = getattr(database_module, class_name)
        instance = database_input_class(*args, **kwargs)

    except (AttributeError, ModuleNotFoundError):
        raise ImportError('{} is not part of our database collection!'.format(database_input_type))
    return instance
