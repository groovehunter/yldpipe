import logging
import pandas as pd
from utils import setup_logger, safe_fn
from fileBase import FileBase
from baseWriter import BaseWriter

logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)


class ExcelWriter(BaseWriter, FileBase):
    """ handles a set of destination files, writes to excel"""
    writer = None

    # XXX wording: file location is not out_fn.
    def __init__(self):
        #self.writer = {}  # XXX where is this from??
        self.buffer = {}
        self.out_fns = []

    def set_dst(self, dst):
        # logger.debug("setting dst to %s", dst)
        self.dst = dst

    def init_writer_all(self):
        # for Excel there is only one dest file
        self.writer = pd.ExcelWriter(self.dst+'.xlsx', engine='xlsxwriter')
        logger.debug("init writer for %s",  self.dst)

    def write(self):
        logger.debug("self.out_fns : %s", self.out_fns)
        for out_fn in self.out_fns:
            sheet_name = safe_fn(out_fn)
            # logger.debug("len buffer[out_fn] : %s", len(self.buffer[out_fn]))
            #logger.debug("cols buffer[out_fn] : %s", self.buffer[out_fn].columns)
            logger.info("write excel sheet %s", sheet_name)
            # logger.debug('buffer[%s].head() : %s', out_fn, self.buffer[out_fn].head())
            try:
                self.buffer[out_fn].to_excel(self.writer, sheet_name=sheet_name, index=False)
                # logger.debug("wrote fields to %s ", sheet_name)
            except Exception as e:
                logger.error("could not write to %s : %s", sheet_name, str(e))
            # logger.debug('empty? : %s', self.buffer[out_fn].empty)
            if self.buffer[out_fn].empty:
                logger.error("buffer is empty for %s", out_fn)
                continue
            # logger.debug('len(buffer[%s]) : %s', out_fn, len(self.buffer[out_fn]))
            for column in self.buffer[out_fn]:
                column_length = max(self.buffer[out_fn][column].astype(str).map(len).max(), len(column))
                #column_length = self.buffer[out_fn][column].astype(str).map(len).max()
                col_idx = self.buffer[out_fn].columns.get_loc(column)
                #column_length = 20
                self.writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length+2)
            """
            """

        self.writer.close()
        #self.writer.save()

    """
    def write_orig(self):
        with pd.ExcelWriter(dstfn, engine='xlsxwriter') as writer:
            for out_fn in self.cfg_si['out_fns']:
                logger.info("write excel sheet %s", sheet_name)
                c = 0
                sheet_name = out_fn
                self.buffer[c].to_excel(writer, sheet_name=sheet_name, index=False)
                # logger.debug("wrote fields to %s : %s", sheet_name, self.fnames[c])
                for column in self.buffer[c]:
                    column_length = max(self.buffer[c][column].astype(str).map(len).max(), len(column))
                    logger.debug("max is %s", column_length)
                    col_idx = self.buffer[c].columns.get_loc(column)
                    writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)
                c += 1
            writer.save()
    """
