from yldpipe.dataBroker import DataBroker
try:
    import win32com.client
except:
    pass
from time import sleep
from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
lg = setup_logger(__name__+'_2', __name__+'_2.log')


class FrameIOandCacheSupport(DataBroker):

    """ Class to support many dataframes IO and caching

    """

    def __init__(self):
        self.df_d = {}
        self.writer_d = {}
        # self.reader_d = {}
        self.buffer_names_d = {}
        self.tkeys_d = {}
        self.frame_fields = {}


    def init_dfio_dicts(self, tkeys):
        for tkey in tkeys:
            # lg.debug('init_dfio_dicts: tkey: %s', tkey)
            self.df_d[tkey] = {}
            self.writer_d[tkey] = {}
            self.buffer_names_d[tkey] = {}

    # XXX own class for table and df support? Or DataBroker better
    def build_fieldlists(self, cfg):
        for key, value in cfg.items():
            if key.endswith('_table'):
                field_list = []
                for e, val in cfg[key].items():
                    # logger.debug('e: %s, val: %s', e, val)
                    if e == 'sort':
                        continue
                    if e == 'add':
                        field_list = field_list + val
                    else:
                        field_list += cfg[e]
                #logger.debug('e: %s, field_list: %s', e, field_list)
                self.__setattr__('fn_'+key, field_list) # deprecated XXX
                self.frame_fields[key] = field_list # NEW
        #lg.debug('self.fn* : %s', [attr for attr in dir(self) if attr.startswith('fn_')])
        #for k, v in self.frame_fields.items():
            #lg.debug('self.frame_fields[%s]: %s', k, v)

    def init_r(self, tkeys):
        self.reader = self.init_reader_class()

    def init_w(self, tkeys):
        self.writer = self.init_writer_class()
        for key in tkeys:
            self.writer_d[key] = self.init_writer_class()

    def close_excel(self):
        try:
            excel = win32com.client.GetObject(None, "Excel.Application")
            # Close the Excel application
            excel.Quit()
            lg.info("Excel application closed successfully.")
        except Exception as e:
            lg.error('Error: %s', e)
        sleep(1)

    def prep_writer(self):
        for tk_i, tk_item in self.tkeys_d.items():
            for tkey in tk_item:
                # XXX os.remove here?
                # lg.debug('prep writer for %s', tkey)
                self.writer_d[tkey].set_outfiles(self.buffer_names_d[tkey].keys())
                self.writer_d[tkey].set_dstfn(self.root_path+'out_'+tkey+'.xlsx')
                # lg.debug('buffer_names_d[%s].keys(): %s', tkey, self.buffer_names_d[tkey].keys())
                #for name in self.buffer_names_d[tkey].keys():
                #    lg.debug('set buffer len=%s for %s', len(self.df_d[tkey[name]]), name)
                #    self.writer_d[tkey].set_buffer(name, self.df_d[tkey][name])
                self.writer_d[tkey].init_writer_all()

    def OLD_prep_writer(self):
        for key in self.cfg_kp_process_fields['xlsx_framedumps']:
            self.writer_d[key].set_dstfn(data_out.joinpath(self.sub, 'out_'+key+'.xlsx'))
            if os.path.exists(self.writer_d[key].dstfn):
                os.remove(self.writer_d[key].dstfn)
            self.writer_d[key].init_writer_all()
        for key in self.cfg_kp_process_fields['xlsx_framedumps_groups']:
            self.writer_d[key].set_dstfn(data_out.joinpath(self.sub, 'out_'+key+'.xlsx'))
            if os.path.exists(self.writer_d[key].dstfn):
                os.remove(self.writer_d[key].dstfn)
            lg.debug('self.writer_d[%s].dstfn: %s', key, self.writer_d[key].dstfn)
            self.writer_d[key].init_writer_all()


    def generic_write_all(self):
        for tk_i, tk_item in self.tkeys_d.items():
            for tkey in tk_item:
                lg.debug('write all for %s', tkey)
                self.writer_d[tkey].set_outfiles(self.buffer_names_d[tkey].keys())
                for bn_key, bn_item in self.buffer_names_d[tkey].items():
                    if self.cfg_kp_logic_ctrl['drop_for_output'] and self.progress_table_output_drop_fields:
                        self.df_d[tkey][bn_key].drop(columns=self.progress_table_output_drop_fields)
                    lg.debug('len buffer %s: %s', bn_key, len(self.df_d[tkey][bn_key]))
                    if (len(self.df_d[tkey][bn_key]) == 0):
                        lg.error('len(self.df_d[%s][%s]) == 0', tkey, bn_key)
                    self.writer_d[tkey].set_buffer(bn_key, self.df_d[tkey][bn_key])
                #lg.debug('self.writer_d[%s].buffer.keys(): %s', tkey, self.writer_d[tkey].buffer.keys())
                self.writer_d[tkey].write()
