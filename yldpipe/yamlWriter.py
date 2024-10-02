#!/usr/bin/python3
import yaml
from common import *
from utils import setup_logger
from config_loader import ConfigLoader
import logging
from baseWriter import BaseWriter

logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)

fields_get_enums = []
fn_file = {}
class YamlWriter(BaseWriter, ConfigLoader):
    def __init__(self):
        self.writer = {}
        self.buffer = {}
        self.fn_out_f = {}

    def init_writer_all(self):
        c = 0
        for out_fn in self.out_fns:
            self.init_writer(out_fn, c)
            c += 1

    def init_writer(self, fn, c):
        """ prepare dict of csv writers for all dest files """
        self.fn_out_f[c] = data_out.joinpath(self.sub + fn + '.yaml')
        logger.debug('fn_out_f: %s', self.fn_out_f[c])


    def write(self):
        c = 0
        for fn in self.out_fns:
            logger.debug('type of df is %s', type(self.buffer[fn]))
            # logger.debug('self.buffer[fn]: %s', self.buffer[fn][:1])
            with open(data_out.joinpath(self.sub+fn+'.yaml'), 'w') as f:
                yaml.dump(self.buffer[fn], f)
            c += 1
