import os
from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
lg = setup_logger(__name__+'_2', __name__+'_2.log')
from time import sleep
from common import data_out, is_windows

if is_windows:
    try:
        import win32com.client
    except:
        pass

class TreeReorderBuilderBase:

    # XXX class YamlConfigSupport:
    # auto create attributes or dict of attrs with same name,
    # the subclass might call that method and overwrite name
    def cache_configs(self):
        fnlist = [
            'kp_wanted_logic',
            'kp_logic_ctrl',
            'kp_term_attr_logic',
            'kp_process_fields',
            'kp_pathmap_backwards',
            'kp_pathmap_true',
        ]
        self.set_configs_as_members(fnlist)
        self.cfg_age = self.load_config_master('vals_a-g-e.yml')
        #self.cfg_meta = self.load_config('kp_meta.yml')
        self.cfg_si = self.load_config('cfg_si.yml')
        # removed
        self.profile_name = self.cfg_si['profile_name']


    def prep_debug_table(self, df):
        # lg.debug('df.columns: %s', df.columns)
        for attr in self.frame_fields['debug_table']:
            if attr not in df.columns:
                lg.debug('attr: %s not in df.columns', attr)
                self.frame_fields['debug_table'].remove(attr)
        df = df[self.frame_fields['debug_table']]
        if 'sort' in self.cfg_kp_process_fields['debug_table'].keys():
            df = df.sort_values(by=self.cfg_kp_process_fields['debug_table']['sort'])
        # lg.debug('df.columns: %s', df.columns)
        return df


    def write_all(self):
        # XXX to specialized:
        # XXX move to treeReorderBase
        self.progress_table_output_drop_fields = self.cfg_kp_process_fields['progress_table_output_drop_fields']
        lg.info('### Writing to excel ###')
        self.generic_write_all()


    def open_excel_files(self):
        # Open the Excel application
        lg.debug('Opening Excel application')
        try:
            #excel = win32com.client.Dispatch("Excel.Application")
            #excel.Visible = True
            lg.info("Excel application opened successfully.")
            success = True
        except Exception as e:
            success = False
            lg.error('Error: %s', e)

        if success:
            sleep(1)
            #for key in self.cfg_kp_process_fields['xlsx_framedumps']:
            #    outfile = data_out.joinpath(self.sub, 'out_' + key + '.xlsx')
            #    workbook = excel.Workbooks.Open(outfile)
            """
            outfile = data_out.joinpath(self.sub, self.cfg_si['out_SI2'])
            workbook1 = excel.Workbooks.Open(outfile)
            sleep(1)
            outfile = data_out.joinpath(self.sub, self.cfg_si['out_SI'])
            workbook2 = excel.Workbooks.Open(outfile)
            sleep(1)
            outfile = data_out.joinpath(self.sub, self.cfg_si['out_matched_entries'])
            workbook3 = excel.Workbooks.Open(outfile)
            """
