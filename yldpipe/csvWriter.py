#!/usr/bin/python3
# import csv
import os
from common import *
from utils import setup_logger
from config_loader import ConfigLoader
from baseWriter import BaseWriter
import logging
logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)

DELIM_IN = ','
fields_get_enums = []
fn_file = {}
class CsvWriter(BaseWriter, ConfigLoader):
    def __init__(self):
        self.writer = {}
        self.buffer = {}
        self.fn_out_f = {}

    def set_dst_dir(self, dst_dir):
        logger.debug('setting dst_dir to %s', dst_dir)
        self.dst_dir = dst_dir
        if not os.path.exists(dst_dir):
            logger.debug('creating dir %s', dst_dir)
            os.makedirs(dst_dir)

    def init_writer_all(self):
        c = 0
        for out_fn in self.out_fns:
            self.init_writer(out_fn, c)
            c += 1

    def init_writer(self, fn, c):
        """ prepare dict of csv writers for all dest files """
        self.fn_out_f[c] = self.dst_dir +'/' + fn + '.csv'
        logger.debug('fn_out_f: %s', self.fn_out_f[c])
        # csvfile = open(self.fn_out_f[c], 'w')
        logger.debug('fn:  %s', fn)

    def write(self):
        c = 0
        for fn in self.out_fns:
            logger.debug('type of df is %s', type(self.buffer[fn]))
            # logger.debug('self.buffer[fn]: %s', self.buffer[fn][:1])
            self.buffer[fn].to_csv(self.dst_dir+fn+'.csv', index=False)
            #self.buffer[fn].to_csv(data_out.joinpath(self.dst_dir, fn, '.csv'), index=False)
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
