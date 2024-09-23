#!/usr/bin/python3
import csv
from common import *
from utils import setup_logger
from config_loader import ConfigLoader
from AbstractBase import AbstractWriter
import logging
logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)

DELIM_IN = ','
fields_get_enums = []
fn_file = {}
class CsvWriter(AbstractWriter, ConfigLoader):
    def __init__(self):
        self.writer = {}
        self.buffer = {}
        self.fn_out_f = {}
    """
    def prep_out(self):
        # load dest fieldnames from cfg files 
        logger.info("load dest fieldnames from cfg files ")
        self.fn_out = {}
        c = 0
        for out_fn in out_fns:
            self.fn_out[c] = data_out.joinpath(self.sub + out_fn)
            c += 1
        # XXX unused
    """

    def init_writer_all(self):
        self.config_dir = str(data_master.joinpath(self.sub))
        self.cfg_si = self.load_config('cfg_si.yml')
        self.out_fns = self.cfg_si['out_fns']
        c = 0
        for out_fn in self.out_fns:
            self.init_writer(out_fn, c)
            c += 1

    def set_dstfn(self, dstfn):
        """ one dstfn makes only sense for Excel """
        pass

    def init_writer(self, fn, c):
        """ prepare dict of csv writers for all dest files """
        self.fn_out_f[c] = data_out.joinpath(self.sub + fn + '.csv')
        logger.debug('fn_out_f: %s', self.fn_out_f[c])
        # csvfile = open(self.fn_out_f[c], 'w')
        logger.debug('fn:  %s', fn)

    def set_buffer(self, fn, buffer):
        logger.debug('set buffer for %s', fn)
        self.buffer[fn] = buffer
    def set_outfiles(self, out_fns):
        self.out_fns = out_fns

    def write(self):
        c = 0
        for fn in self.out_fns:
            logger.debug('type of df is %s', type(self.buffer[fn]))
            # logger.debug('self.buffer[fn]: %s', self.buffer[fn][:1])
            self.buffer[fn].to_csv(data_out.joinpath(self.sub+fn+'.csv'), index=False)
            c += 1

"""
class CsvOrigWriter(CsvWriter):
    def __init__(self):
        super().__init__()

    def init_writer(self, fn, c):
        self.fn_out_f[c] = data_out.joinpath(self.sub + fn +'.csv')
        self.csvfile = open(self.fn_out_f[c], 'w', newline='')
        self.writer[c] = csv.DictWriter(self.csvfile, fieldnames=self.cfg_fnames['fnames'+str(c)], delimiter=DELIM_IN)
        self.writer[c].writeheader()
        logger.debug('fn:  %s', fn)
    def write(self):
        c = 0
        for fn in self.out_fns:
            self.writer[c].writerows(self.buffer[fn])
            c += 1
"""
