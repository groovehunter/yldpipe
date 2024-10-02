import logging

from dataBroker import DataBroker
from config_loader import ConfigLoader
# from storage import StorageHandler
from common import data_master
from utils import setup_logger
logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)

class DataPipeline(DataBroker):
    """ the main class for the data pipeline;
    Initiates the reader, writer"""
    # array of fieldnames
    fn_index = 0
    out_fns = []

    def work_meta(self):
        logger.debug('mode is %s', self.cfg_profile['mode'])
        self.mode = self.cfg_profile['mode']
        parts = self.mode.split('_')
        logger.debug('parts: %s', str(parts))
        if len(parts) == 2:
            func, sub = parts
            eval_str = 'self.%s("%s")' % (func, sub)
        else:
            func = self.mode
            eval_str = 'self.%s()' % (func)
        logger.debug(eval_str)
        # CALL the subfunctions
        eval(eval_str)

    def si(self, sub):
        self.sub = 'SI/'
        self.app = 'SI'
        self.config_dir = str(data_master.joinpath(self.sub))
        self.reader = self.init_reader_class()
        self.writer = self.init_writer_class()
        fn = 'config_fnames.yml'
        self.cfg_fnames = self.load_config(fn)
        fn = 'cfg_si.yml'
        self.cfg_si = self.load_config(fn)
        self.reader.setatt(cfg_si=self.cfg_si,
                           sub=self.sub,)
        if self.cfg_profile['transform']:
            fn_cfg = 'config_meta.yml'
            self.meta = self.load_config(fn_cfg)

        self.reader.init_reader()
        # WORK - forking here in sub-methods
        eval('self.'+self.mode+'()')

        self.writer.write()
        self.report()

    def si_1to1(self):
        # XXX needs collect_unknown_values() too
        self.fieldnames_dict = self.reader.get_all_sheet_fieldnames()
        self.collect_unknown_values()
        if self.cfg_profile['reader'] == 'excel':
            self.reader.read_all()
        # in 1to1 mode out_fn names are the same as in_fn names
        self.writer.set_outfiles(self.cfg_si['in_fns'])
        # XXX minimize the following
        self.writer.setatt(cfg_si=self.cfg_si,
                           config_dir=self.config_dir,
                           sub=self.sub)
        self.writer.set_dst(self.cfg_si['out_SI'])
        self.writer.init_writer_all()

        # WORK
        self.loop_items()

    def si_split(self):
        self.reader.read_all()
        # fnames from the first sheet
        fn_in = self.cfg_si['in_fns'][0]
        self.fieldnames_dict[fn_in] = self.reader.get_fieldnames(fn_in)

        #fn_out = self.cfg_si['out_fns'][0]
        self.fieldnames_avail = self.fieldnames_dict[fn_in]
        self.collect_unknown_values()

        self.reader.read_first()
        sheet_nr = self.cfg_profile['default_sheet_nr']
        buffer_id = self.cfg_si['in_fns'][sheet_nr]

        # buffer_id = self.reader.sheet_names[sheet_nr]
        logger.debug('buffer_id: %s', buffer_id)
        buffer_in = self.reader.get_buffer(buffer_id)
        # set fnames source
        if self.cfg_profile['fnames_src'] == 'config':
            self.fieldnames_cur = self.cfg_fnames['fnames0']
        elif self.cfg_profile['fnames_src'] == 'data':
            self.fieldnames_cur = list(buffer_in)

        self.loop_rows_and_split_only(buffer_in)

        self.writer.setatt(cfg_si=self.cfg_si,
                           sub=self.sub)
        self.writer.set_dstfn(self.cfg_si['out_SI'])
        self.writer.init_writer_all()
        self.writer.set_outfiles(self.cfg_si['out_fns'])
        for out_fn in self.cfg_si['out_fns']:
            logger.debug('set buffer in writer: %s with len %d', out_fn, len(self.arr_df[out_fn]))
            # logger.debug('cols of buffer[%s] : %s', out_fn, self.arr_df[out_fn].columns)
            self.writer.set_buffer(out_fn, self.arr_df[out_fn])

    def ex2an(self):
        self.excel2ansible()
    def excel2ansible(self):
        self.sub = 'ansible/'
        self.sub_in = 'SI/'
        self.sub_out = 'ansible/'
        self.app = 'ansible'
        self.config_dir = str(data_master.joinpath(self.sub))
        # self.reader = ExcelReader()
        # self.writer = AnsibleInvWriter()
        self.reader = self.init_reader_class()
        self.writer = self.init_writer_class()

        fn = 'config_fnames.yml'
        self.cfg_fnames = self.load_config(fn)
        fn = 'cfg_si.yml'
        self.cfg_si = self.load_config(fn)
        self.reader.setatt(cfg_si=self.cfg_si,
                           sub=self.sub_in,)
        self.reader.init_reader()
        self.reader.read_all()
        self.writer.setatt(cfg_si=self.cfg_si,
                           sub=self.sub_out,
                           config_dir=self.config_dir)
        # NOT NEEDED # self.writer.set_dstfn(self.cfg_si['out_SI'])
        # set input and output to just one data file resp table data
        self.writer.init_writer_all()
        # logger.debug('data is %s', self.data.head())
        self.data = self.reader.get_buffer(self.cfg_si['out_fns'][0])
        fields_wanted = ['Servername', 'Rolle', 'IP_Adresse']
        criteria = "data['Rolle'].str.contains('_')"
        data = self.filter_rows_by_crit(self.data, criteria)
        buffer_out = self.reduce_data(data, fields_wanted)
        # for now
        self.writer.set_buffer(self.cfg_si['out_fns'][0], buffer_out)
        self.writer.df2inventory()

        self.writer.write()

    def csv2excel(self):
        raise NotImplementedError
    def report(self):
        print("DataPipeline report")
        print("reader: ", self.reader)
        print("writer: ", self.writer)
        print("Mode: ", self.cfg_profile['mode'])
