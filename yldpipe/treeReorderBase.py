from tokenize import group

import pandas as pd
import yaml
from YamlConfigSupport import YamlConfigSupport
from common import data_master, data_out, data_in

from shutil import copyfile
from random import randint
from utils import setup_logger
import logging

from yldpipe.dataBroker import DataBroker

logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
lg = setup_logger(__name__+'_2', __name__+'_2.log')

class TreeReorderBase(DataBroker):  # YamlConfigSupport):

    def __init__(self) -> None:
        self.sub = 'bmarks/'
        self.config_dir = str(data_master.joinpath(self.sub))
        self.config_dir_master = str(data_master)
        self.dt_fn = 'kp_tree_team.yml'
        self.dt_d = self.load_config(self.dt_fn)
        # logger.debug('self.dt_d: %s', self.dt_d)
        logger.info("-----------------------------------------------")

    def stats_df_init(self):
        self.df_d['stats']['report'] = pd.DataFrame(columns=self.frame_fields['stats_table'])
        self.buffer_names_d['stats']['report'] = 'report'

    def stats_init(self):
        self.count = 0
        self.count_suc = 0
        self.count_err = 0
        self.count_crit = 0
        self.results = {
            'crit': [],
            'err': [],
        }

    # XXX move to own feature class
    def stats_report(self, name=''):
        logger.info("------  ------    STATS REPORT: %s", name)
        logger.info("self.count : %s", self.count)
        logger.info("self.count_suc: %s", self.count_suc)
        logger.info("self.count_crit: %s", self.count_crit)
        logger.info("self.count_err: %s", self.count_err)
        ldf = len(self.df_d['stats']['report'])
        lg.debug('len(self.df_d[stats][report]): %s', ldf)
        self.df_d['stats']['report'].loc[ldf] = {
            'name': name,
            'count': self.count,
            'count_suc': self.count_suc,
            'count_err': self.count_err,
            'count_crit': self.count_crit,
        }

    def set_src(self, db_path, pw):
        lg.debug('db_path: %s', db_path)
        self.db_path = db_path
        self.pw = pw
        fp = data_in.joinpath(self.sub, self.cfg_si['db_src'])
        self.kp_src = self.init_storage_src_class()
        self.kp_src.set_src(fp)
        attrs = self.cfg_kp_process_fields['kp_old_fields'] + self.cfg_kp_process_fields['kp_same_fields']
        self.kp_src.create_tree_from_json(attrs)
        #self.kp_src._import()
        # export discovered tree to yaml
        fp = data_out.joinpath(self.sub, self.cfg_si['tree_original_export_fn'])
        self.kp_src.export(fp, format='pure_hierarchy')

    def set_dst(self):
        fp = data_out.joinpath(self.sub, self.cfg_si['db_dst'])
        self.kp_dst = self.init_storage_dst_class()
        self.kp_dst.set_src(fp)

        fp = data_master.joinpath(self.sub, self.dt_fn)
        self.kp_dst.load_hierarchy_from_yaml(fp)
        attrs = self.cfg_kp_process_fields['kp_old_fields'] + self.cfg_kp_process_fields['kp_same_fields']
        self.kp_dst.create_tree_from_yaml(self.kp_dst.yaml, attrs)


    def add_df_to_new_tree(self, df):
        lg.debug('len(df): %s', len(df))
        for i, row in df.iterrows():
            group_dst = self.kp_dst.find_groups_by_path(row['group_path_new'])
            self.try_adding(group_dst, row)

    # XXX provide df as argument to method ?
    def add_to_new_tree(self, case_name):
        attr_needed = ['group_path_new', 'title_new', 'username_new', 'password', 'url', 'notes', 'fk']
        df = self.df_wanted[case_name]
        df_found = df[df['status'].str.contains('FOUND')]
        lg.debug('len(df): %s, len(df_found): %s', len(df), len(df_found))

        for i, row_ser in df_found[attr_needed].iterrows():
            row = row_ser.to_dict()
            group_dst = self.kp_dst.find_groups_by_path(row['group_path_new'])
            logger.debug(row)
            self.try_adding(group_dst, row)
            # logger.debug('group_path_new: %s, group_dst: %s', row['group_path_new'], group_dst)


    def try_adding(self, group_dst, row):
        lg.error("XXXXXXXXXXXXXXXXXX NOT IMPLEMENTED XXXXXXXXXXX")
        pass

    # def create_new_etree_rec_from_dict(self, data):
    def create_new_etree_rec_from_dict(self):
        """ create new kp tree and walk tree to work on entry transfer """
        # lg.debug('self.sub: %s', self.sub)
        # copy empty DB file to dest db file, for fresh start
        db_path_empty = data_master.joinpath(self.sub, self.cfg_si['db_file_empty'])
        db_path_dst = data_out.joinpath(self.sub, self.cfg_si['db_file_dst'])
        db_path_dst_s = str(db_path_dst)
        copyfile(db_path_empty, db_path_dst)

        """
        empty = { 'root': {} }
        # lg.debug('empty: %s', empty)
        with open(db_path_dst_s, 'w') as f:
            yaml.safe_dump(empty, f)
        with open(db_path_dst_s, 'r') as f:
            self.kp_dst = yaml.safe_load(f)
        # lg.debug('self.kp_dst: %s', self.kp_dst)
        """

