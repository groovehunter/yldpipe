import logging
import csv
from AbstractBase import AbstractReader
import pandas as pd
from utils import setup_logger
from common import data_in

logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)
DELIM_IN = ','


class CsvReader(AbstractReader):
    """ access a set of files as input """
    cfg_si = {}
    reader = {}

    def __init__(self):
        self.buffer = {}

    def init_reader(self):
        logger.debug('opening file %s', self.fn_in)
        pass

    def get_fieldnames(self, fn=None):
        """ read first sheet and return col names """
        if not fn: fn = self.cfg_si['out_fns'][0]
        self.fieldnames = list(self.buffer[fn])
        return self.fieldnames

    def read(self, fn):
        file_path = data_in.joinpath(self.sub + fn + '.csv')
        self.buffer[fn] = pd.read_csv(file_path)

    def read_all(self):
        for fn in self.cfg_si['out_fns']:
            self.read(fn)

    def get_buffer(self, fn):
        return self.buffer[fn]


class CsvOrigReader(CsvReader):

    def __init__(self):
        super().__init__()

    def init_reader(self):
        c = 0
        for fn in self.cfg['out_fns']:
            self.fn_in = data_in.joinpath(self.sub + fn)
            self.csvfile = open(self.fn_in, encoding='utf-8-sig', newline='')
            self.reader[fn] = csv.DictReader(self.csvfile, delimiter=DELIM_IN)
            self.fnames_in[c] = self.reader.fieldnames
            self.fnames_out[c] = self.fnames_in[c].copy()
            logger.info("fnames_in/out nr. %s : %s", c, self.fnames_out[c])
            c += 1

    def read(self, fn):
        file_path = data_in.joinpath(self.sub + fn + '.csv')
        self.reader[fn].read(file_path)

