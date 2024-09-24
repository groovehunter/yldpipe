import pandas as pd
from collections import namedtuple
from numpy.ctypeslib import load_library
from yldpipe.frameIOandCacheSupport import FrameIOandCacheSupport
from treeReorderBase import TreeReorderBase
from treeReorderBuilderBase import TreeReorderBuilderBase
from treeReorderBuilderWanted import TreeReorderBuilderWanted
from transformFunc import TransformFunc
from SICache import SICache
from common import data_master
from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
lg = setup_logger(__name__+'_2', __name__+'_2.log')
from creds import db_path, pw
from common import is_windows, data_out
from random import randint

if is_windows:
    try:
        import win32com.client
    except:
        pass

class TreeReorderBuilder(TreeReorderBase, TreeReorderBuilderWanted, TreeReorderBuilderBase,
                         FrameIOandCacheSupport, TransformFunc, SICache):

    def __init__(self):
        self.sub = 'bmarks/'
        FrameIOandCacheSupport.__init__(self)
        TreeReorderBase.__init__(self)
        # self.config_dir = data_master.joinpath('keepass')
        self.buffer_names = {}
        # XXX not needed up to now
        SICache.__init__(self)

        # legacy
        # XXX move to KeepassBuilderBase ? IO related
        self.si_data = None

        self.cache_configs()

        self.df_d['entries_old'] = {}
        self.buffer_names_d['entries_old'] = {}

        self.close_excel()

        self.root_path = str(data_out.joinpath(self.sub))

    def init_framecache(self):
        xlsx_groups = [
            'xlsx_framedumps',
            'xlsx_framedumps_groups',
            'xlsx_framedumps_others',
        ]
        tkeys_d = {}
        c = 0
        for group in xlsx_groups:
            tkeys = self.cfg_kp_process_fields[group]
            # lg.debug('initializing dicts keys=%s for frameIO group: %s', tkeys, group)
            self.init_dfio_dicts(tkeys)
            if not self.cfg_profile['reader'] is None:
                self.init_r(tkeys)  # not used for this app
            if not self.cfg_profile['writer'] is None:
                self.init_w(tkeys)
            tkeys_d[c] = tkeys
            c += 1
        self.tkeys_d = tkeys_d

        self.prep_writer()

    def init_storage_and_fields_TMP(self):
        # XXX move to KeepassBuilderBase
        # self.in_SI = data_in.joinpath(self.sub, self.cfg_si['in_SI'])
        # source DB
        self.set_src(db_path=db_path, pw=pw)
        self.set_dst()
        # self.create_new_etree_rec_from_dict()
        lg.info('Loaded keepass DB at %s', db_path)
        self.build_fieldlists(self.cfg_kp_process_fields)

    def main_flow_ctrl(self):
        self.stats_df_init()
        work = self.cfg_kp_logic_ctrl['work']
        ### logic for WANTED entries
        if 'dump_group_entries' in work:
            self.allgroups_age_dump_entries()
            self.allgroups_hs_dump_entries() # ?

        if 'loop_sandbox' in work:
            self.allgroups_wanted_loop_sandbox()
        if 'loop_unknown' in work:
            self.allgroups_wanted_loop_unknown()

        if 'allgroups_old_match' in work:
            group_list = self.cfg_kp_logic_ctrl['loop_crit']
            self.allgroups_old_match(group_list)
            #group_list = self.cfg_kp_logic_ctrl['loop_hostspecific']
            #self.allgroups_old_match(group_list)

        self.buffer_names_d['wanted'] = {}
        if 'loop_crit' in work:
            groups_new = self.cfg_kp_logic_ctrl['loop_crit']
            self.allgroups_age_do_cases(groups_new)
        # XXX if cfg flag:
        # all cases do:
        # add_to_new_tree('case_name')
        if 'loop_hostspecific' in work:
            #self.allgroups_hs_do()
            groups_new = self.cfg_kp_logic_ctrl['loop_hostspecific']
            self.allgroups_hs_do_cases(groups_new)

        ### OTHER logic
        self.allgroups_others_do()

        # I/O - Write all tables to excel
        if 'write_all' in work:
            lg.debug('write_all')
            self.write_all()
        if 'open_files' in work:
            self.open_excel_files()

        if 'add_age_to_tree' in work:
            lg.debug('add_age_to_tree - UNUSED')
            #self.insert_into_tree()
            #self.allgroups_wanted_add_to_new_tree()

        if 'save_tree' in work:
            self.kp_dst.save()

        lg.debug('END of work: %s', self.cfg_kp_logic_ctrl['work'])


    def allgroups_others_do(self):
        work = self.cfg_kp_logic_ctrl['work']

        if 'loop_copyall' in work:
            group_list = self.cfg_kp_logic_ctrl['loop_copyall']
            logger.debug('group_lists: %s', group_list)
            for group_name in group_list:
                # group_name is a path, XXX refactor
                path_src = group_name  # because it is a root path
                lg.debug('for groupname: %s path_src: %s', group_name, path_src)
                path_dst = self.cfg_kp_pathmap_true.get(group_name, group_name)
                lg.debug('for groupname: %s path_dst: %s', group_name, path_dst)
                group_src = self.kp_src.find_groups_by_path(path_src)
                group_dst = self.kp_dst.find_groups_by_path(path_dst)
                group_logic = self.cfg_kp_wanted_logic.get(group_name, None)
                if (group_src and group_dst):
                    self.group_do_entries_copyall(group_src, group_dst, group_logic)
        # XXX both  copy methods can be one DRY, flag if subgroups?

        if 'loop_copyall_rec' in work:
            group_list = self.cfg_kp_logic_ctrl['loop_copyall_rec']
            lg.debug('group_lists: %s', group_list)
            for group_name in group_list:
                path = group_name
                lg.debug('path is %s', path)
                group_src = self.kp_src.find_groups_by_path(path)
                group_dst = self.kp_dst.find_groups_by_path(path)
                group_logic = self.cfg_kp_wanted_logic.get(group_name, None)
                lg.debug('group_src: %s, group_dst: %s', group_src, group_dst)
                if not (group_src and group_dst):
                    lg.error('group_dst or group_src not found: %s', group_name)
                    continue
                self.group_do_entries_copyall(group_src, group_dst, group_logic)
                if group_src.subgroups:
                    for sub_group in group_src.subgroups:
                        lg.debug('XXX TODO recursion for subgroups: %s', sub_group)


    def group_do_entries_copyall(self, group_src, group_dst, group_logic):
        df = pd.DataFrame(columns=self.frame_fields['progress_sm_table'])
        # if transform:
        # syntax from transformFunc ?? not needed i think
        c, rc_suc, rc_err = 0,0,0
        attrs = self.cfg_kp_process_fields['kp_old_fields'] + self.cfg_kp_process_fields['kp_same_fields']

        # XXX use stats from KeepassBase
        #logger.debug('entries count: %s', len(group_src.entries))
        # XXX use dataframe to update the table
        #for entry in group_src.entries:
        logger.debug('entries count: %s', len(group_src.children))
        for entry in group_src.children:
            row = {}
            for attr in attrs:
                attr_value = getattr(entry, attr)
                row[attr] = attr_value

            row['group_path_new'] = group_dst.path
            # logger.debug('group_dst.path: %s', group_dst.path)
            # logger.debug(row)
            try:
                self.kp_dst.add_entry(group_dst, row)
                row['status'] = 'OK: Entry copied'
                # logger.debug('OK entry copied: %s | %s', entry.title, entry.username)
                rc_suc += 1
            except:
                row['status'] = 'ERROR: Entry not copied'
                logger.error(row)
                rc_err += 1
            ldf = len(df)
            df.loc[ldf] = row
            c += 1

        logger.debug('copied successful %s entries, failed %s entries', rc_suc, rc_err)


    def groups_map_new_to_old(self, group_name_new):
        logic_pathmap_backwards = self.cfg_kp_pathmap_backwards.get(group_name_new, None)
        # lg.debug('logic_pathmap_backwards : %s', logic_pathmap_backwards)
        if logic_pathmap_backwards is None:
            return group_name_new
        if 'old' in logic_pathmap_backwards.keys():
            group_name_old = logic_pathmap_backwards['old']
        else:
            group_name_old = logic_pathmap_backwards
        return group_name_old

