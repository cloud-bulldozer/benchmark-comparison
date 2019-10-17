from abc import ABCMeta, abstractmethod


class DatabaseBaseClass(metaclass=ABCMeta):
    def __init__(self):
        self._dict = None

    @abstractmethod
    def emit_values_dict(self):
        pass
