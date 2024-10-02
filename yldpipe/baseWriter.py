from AbstractBase import AbstractWriter
from utils import setup_logger
import logging
logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)


class BaseWriter(AbstractWriter):
    def set_buffer(self, fn, buffer):
        self.buffer[fn] = buffer

    def set_dst(self, dst):
        if self.__class__.__name__ == 'CsvWriter':
            basename = dst.split('.')[0] # XXX improve
            self.set_dst_dir(basename)
        else:
            self.set_dst_fn(dst)

    def set_outfiles(self, out_fns):
        self.out_fns = out_fns

    def init_writer(self, out_fn):
        pass

    def writerow(self, row):
        pass

