#!/usr/bin/python3
import json
from common import *
from utils import setup_logger
from config_loader import ConfigLoader
from AbstractBase import AbstractWriter
import logging
logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)

fields_get_enums = []
fn_file = {}
class JsonWriter(AbstractWriter, ConfigLoader):
    def __init__(self):
        self.writer = {}
        self.buffer = {}
        self.fn_out_f = {}

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
        self.fn_out_f[c] = data_out.joinpath(self.sub + fn + '.yaml')
        logger.debug('fn_out_f: %s', self.fn_out_f[c])

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
            with open(data_out.joinpath(self.sub+fn+'.yaml'), 'w') as f:
                json.dump(self.buffer[fn], f)
            c += 1
