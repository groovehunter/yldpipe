from abc import ABC, abstractmethod


class AbstractReader(ABC):
    in_SI = None

    @abstractmethod
    def read(self, fn):
        pass

    @abstractmethod
    def get_fieldnames(self, fn):
        """ read sheet named fn and return col names """
        pass


class AbstractWriter(ABC):
    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def init_writer(self):
        pass

    @abstractmethod
    def set_dst(self, dstfn):
        pass

    @abstractmethod
    def set_outfiles(self, out_fns):
        """ set the names of the output files or sheets """
        pass

    @abstractmethod
    def set_buffer(self, fn, buffer):
        """ Abstract method for setting the buffer."""
        pass


class AbstractStorage(ABC):
    @abstractmethod
    def find_groups_by_path(self, path):
        pass

    @abstractmethod
    def find_entry_by_path(self, path):
        pass

    def load_hierarchy(self, path):
        pass
