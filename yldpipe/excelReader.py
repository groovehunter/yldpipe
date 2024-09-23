import logging
import pandas as pd
from common import data_in
from utils import setup_logger
from AbstractBase import AbstractReader
from fileBase import FileBase

logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)


class ExcelReader(AbstractReader, FileBase):
    """ A class to read an Excel file """
    data = None
    fieldnames_dict = {}
    sheet_names = []
    cfg_si = {}
    sub = ''

    def __init__(self):
        self.buffer = {}
        self.cfg_si = {}

    def get_all_sheet_fieldnames(self):
        self.fn = self.cfg_si['in_fns'][0]
        if not self.buffer.keys():
            self.read_all()
        return self.fieldnames_dict

    def get_fieldnames(self, fn):
        """ read first sheet and return col names """
        if not self.buffer.keys():
            df = pd.read_excel(self.in_SI, sheet_name=fn, engine='openpyxl')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            self.buffer[fn] = df
        self.fieldnames_dict[fn] = list(self.buffer[fn])
        # logger.debug('fieldnames_dict: %s', self.fieldnames_dict)
        return self.fieldnames_dict[fn]

    def init_reader(self):
        self.in_SI = data_in.joinpath(self.sub, self.cfg_si['in_SI'])

    def read_first(self):
        logger.debug('self.cfg_si: %s', self.cfg_si)
        self.read(self.cfg_si['in_fns'][0])

    def read(self, fn):
        self.buffer[fn] = pd.read_excel(self.in_SI, sheet_name=fn, dtype='str', engine='openpyxl')

    def read_all(self):
        logger.debug('reading from file %s', self.in_SI)
        self.sheet_names = []
        for fn in self.cfg_si['in_fns']:
            sheet_name = fn
            self.sheet_names.append(sheet_name)
            df = pd.read_excel(self.in_SI, sheet_name=sheet_name, dtype='str', engine='openpyxl')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            self.buffer[sheet_name] = df
            self.fieldnames_dict[fn] = list(self.buffer[fn])
            logger.debug('read sheet %s, len is %s', sheet_name, len(self.buffer[sheet_name]))
            # logger.debug('head of sheet %s is %s', sheet_name, self.buffer[sheet_name].head())

    def get_buffer(self, out_fn):
        sheet_name = out_fn
        logger.debug('buffer keys are %s, we want %s', self.buffer.keys(), out_fn)
        logger.debug('sheet %s, len is %s', sheet_name, len(self.buffer[sheet_name]))
        return self.buffer[sheet_name]
