import logging
from common import *
from utils import setup_logger
from transformFunc import TransformFunc
from dataPipeline import DataPipeline
import pandas as pd

logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)

# fn = data_in.joinpath('keepass/old_entries.csv')
fn = data_in.joinpath('SI/Server_Infrastruktur_FG.csv')


# inherit from DataPipelineSupport which has the methods to choose
# the mode and various work methods
class DataLooper(TransformFunc, DataPipeline):
    """ A class to loop through all rows of a csv file
        and apply transformations """
    DELIM_IN = ','
    pkey = 'Servername'
    fieldnames_dict = {}
    fields_get_enums = []
    config_dir = ''
    dp = None
    rcount = 0
    reader, writer = None, None

    def __init__(self):
        # self.trF = TransformFunc()
        # self.fnames = {}
        self.count_skipped = 0
        self.count_replaced = 0
        self.unique_list = {}

    def collect_unknown_values(self):
        """ collect all values that are not in the meta """
        fnx = self.cfg_si['in_fns'][0]
        for f in self.fieldnames_dict[fnx]:
            if self.meta.get(f):
                cmd = list(self.meta[f].keys())[0]
                if cmd == 'collect':
                    self.fields_get_enums.append(f)
        for f in self.fields_get_enums:
            self.unique_list[f] = []


    def loop_items(self):
        """ loop all entities needed processing: ie each csv file / sheet
            to its own dest file /sheet; Used for 1to1 mode """
        for fnx in self.cfg_si['in_fns']:
            buffer_in = self.reader.get_buffer(fnx)
            if self.cfg_profile['transform']:
                buffer_out = self.transform_sheet(buffer_in)
                logger.debug('loop result buffer, len is %d', len(buffer_out))
            else:
                buffer_out = buffer_in
            # work done
            self.writer.set_buffer(fnx, buffer_out)

    def transformF(self, field):
        def inner(value):
            if field == self.pkey and value.startswith('#'):
                logger.info(value)
                return value
            my = self.gener(value, self.meta[field], field)
            return my
        return inner

    def transform_sheet(self, data):
        """ perform the validation on the table """
        data = data.fillna('')
        for column in data.columns:
            # logger.info('work on column %s', column)
            if not self.meta[column]:
                continue
            data[column] = data[column].apply(self.transformF(column))
        return data

    def check_if_comment_row(self, row):
        # special treatment for empty rows or header rows
        pk_val = getattr(row, self.pkey)
        # logger.debug("val type %s", type(pk_val))
        comment_row = (
                isinstance(pk_val, float) or
                (isinstance(pk_val, str) and
                 pk_val.startswith('#'))
        )
        if comment_row:
            self.count_skipped += 1
            if (isinstance(pk_val, str) and
                    pk_val.startswith('#')):
                # logger.debug("HEADLINE: pkey val is %s", pk_val)
                return pk_val

            return True
        else:
            return False

    def filter_rows_by_crit(self, data, criteria):
        """ filter rows by criteria """
        data = data.fillna('')
        logger.debug("criteria: %s", criteria)
        ev_str = "data[%s]" % criteria
        data = eval(ev_str)
        return data

    def reduce_data(self, data, fields_wanted):
        data = data.fillna('')
        data = data[fields_wanted]
        # logger.debug('head of df: %s', data.head())
        return data
    def create_sub_dataframe(self, df, col_names):
        return df[col_names]

    def loop_rows_and_split_only(self, data):
        fnames = self.cfg_fnames
        data = data.fillna('')
        data = self.transform_sheet(data)
        arr_df = {}
        cc = 0
        for out_fn in self.cfg_si['out_fns']:
            logger.debug('fnames[%d] are %s', cc, fnames['fnames'+str(cc)])
            arr_df[out_fn] = self.create_sub_dataframe(data, fnames['fnames'+str(cc)])
            cc += 1
        self.arr_df = arr_df


    def report(self):
        print("------------------ REPORT ")
        print("count_skipped: ", self.count_skipped)
        print("count_replaced: ", self.count_replaced)
        print("row count: ", self.rcount)
        c = 0
        print(self.cfg_si['out_fns'])
        for out_fn in self.cfg_si['out_fns']:
            fname = 'fnames'+str(c)
            if fname in self.cfg_fnames:
                logger.debug("=== fnames[%d]", c)
                logger.debug(self.cfg_fnames[fname])
            c += 1

    # list all possible values to collect
    def all_values(self):
        for f in self.fields_get_enums:
            self.unique_list[f].sort()
