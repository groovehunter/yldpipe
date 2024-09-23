#!/usr/bin/python3 
import re
import logging
from config_loader import ConfigLoader
from common import data_out, data_master
from creds import db_path, pw
from pprint import pprint
from shutil import copyfile
from utils import setup_logger
from pykeepass import PyKeePass
#from tree_mapper import TreeMapper
from treeReorderBase import TreeReorderBase

logger = setup_logger(__name__, __name__+'.log', logging.DEBUG)


class treeReorderExporter(TreeReorderBase):
    def __init__(self):
        super().__init__()
        self.attrs_e = [
          'title', 'group', 'parentgroup', 'path', 'username'
        ]
        self.attrs_g = [
          'name', 'group', 'parentgroup', 'subgroups', 'is_root_group', 'path',
        ]

class Mapper:
    def __init__(self, entries, dst):
        self.entries = entries
        self.dst = dst


class treeReorderReader(TreeReorderBase, TreeMapper):
    """ class for transfer of all entries of a kp DB to a new DB file with 
      changed group hierarchy """
    dt_fn = None

    def __init__(self):
        # super().__init__(self)
        TreeReorderBase.__init__(self)
        TreeMapper.__init__(self)
        self.stats_init()
        # self.stats_report()

        # cfg data sources
        self.cfg_si = self.load_config('cfg_si.yml')
        self.pathmap = self.load_config('kp_pathmap.yml')
        self.entries_map = self.load_config('kp_entries_map.yml')
        # XXX set_pykeepass_db is called in KeepassBase
        self.set_src(db_path, pw)
        logger.debug('Loaded keepass DB at %s', db_path)
        logger.debug('root_group: %s', self.kp_src.root_group)

    def prep_transfer(self):
        self.create_new_etree_rec_from_dict()
        self.mapperlist = []

    def work_entries(self, node):
        if node.name == 'eip':
            return
        dst = self.resolve_dest_hgnode(node)
        if dst is None:
            return
        logger.debug("dst: %s, entry len: %d", dst.name, len(node.entries))
        m = Mapper(node.entries, dst)
        self.mapperlist.append(m)
        # self.add_entries_in_group(node.entries, dst)
        # node.dest = dst
        return 

    def cleanup_entries(self, entries, dst_g):
        cfg = self.entries_map.get(dst_g.name, None)
        if not cfg:
            return
        logger.debug('cleanup for group: %s', dst_g.name)
        # logger.debug('cfg: %s', cfg)
        var = {
            'host': r'(?:vm|ph)\d{5}',
            'ger': r'[A-Za-z]{4}',
            'crit': r'[A-Z][a-z]{3,4}',
            'crit2': r'[a-z]{3}',
            }

        for prepat in cfg:
            pat = re.sub(r'\{([^}]+)}', lambda m: var[m.group(1)], prepat)

            logger.debug('prepat %s', prepat)
            logger.debug('pat is %s ', pat)
            cpat = re.compile(pat)
            cs, ce = 0, 0
            # accumulate those entries which never matched, use dict 
            # err = []
            for entry in entries:
                m = cpat.match(entry.title)
                if m:
                    # logger.debug('on title %s', entry.title)
                    logger.debug("M: %s == %s", m.groups(), entry.title)
                    cs += 1
                else:
                    ce += 1
            logger.debug("tot: %s, suc: %d, err: %d", cs+ce, cs, ce)
            # if err:
            #    logger.debug("err: %s", err)

    def work_mapper(self):
        logger.debug('START working on mapperlist, len=%d', len(self.mapperlist))
        for m in self.mapperlist:
            self.cleanup_entries(m.entries, m.dst)
            # self.add_entries_in_group(m.entries, m.dst)


    def aaresolve_dest_hgnode(self, subhg):
        pathmap = self.pathmap
        name = subhg.name
        logger.debug("searching %s ", subhg.name)
        # step 0 exceptions, remove
        if name in pathmap['skip']:
            logger.info("SKIPPED %s", name)
            return None
        if name in pathmap['check']:
            val = pathmap['check'][name]
            # logger.debug("val %s ", val )
            if val == 'reverse_path':
                path = subhg.path
                path.reverse()
                logger.debug("path %s ", path)
                dest = self.kp_dst.find_groups_by_path(path)
                return dest
        # main     
        if name not in pathmap.keys():
            logger.error("missing config for %s", name)

        val = pathmap[name]
        logger.debug("val %s ", val )
        if val is None:
            val = name
        try:
            res = self.kp_dst.find_groups(name=val)
            # logger.debug("res %s ", res )
            if len(res) == 1:
                dest = res[0]
                # logger.debug("dest %s ", dest )
                return dest
            else:
                dest = res[0]
                logger.debug("resolved RES %s  === chose first", res)
                return dest
        except:
            logger.error("RES ERROR")
            dest = self.dest_fallback
            return dest

    def add_entry_title_changed(self, entry, dst_g):
        done = False
        lfd = 0
        while not done:
            title = 'MOVED_'+str(lfd)+'_'+entry.title
            username = 'MOVED_'+str(lfd)+'_'+entry.username
            logger.debug("EXCEPTION, %s - %s, %s", dst_g, title, username)
            try:
                ne = self.kp_dst.add_entry(dst_g, title, username, entry.password)
                logger.debug("MOVED - adding entry %s ", e.title)
                done = True
                break
            except:
                lfd += 1
                logger.debug("lfd %s ", str(lfd))
                if lfd > 20:
                    done = True
                    logger.critical("Some error: %s, %s", title, username)
                    self.count_crit += 1
                    self.results['crit'].append(str(entry))
                    lfd = 0

    def add_entries_in_group(self, entries, dst_g):
        logger.debug("Found dst group/s : %s", dst_g)
        for e in entries:
            self.count += 1
            if e.username is None:
                # logger.warning("username was None: %s", e)
                e.username = ''
            if e.title is None:
                logger.warning("title was None: %s", e)
                e.title = 'TODO'
            try:
                ne = self.kp_dst.add_entry(dst_g, e.title, e.username, e.password)
                # logger.debug("adding entry %s ", e)
                self.count_suc += 1
            except:
                # logger.debug("FAILED 1st - adding entry %s ", e)
                self.results['err'].append(str(e))
                self.count_err += 1
                # self.add_entry_title_changed(e, dst_g)

    def walk_etree(self, node, work=False):
        logger.debug("proc group: %s  -- %s", node.name, node.path)
        for subg in node.subgroups:
            logger.debug("processing group: %s  ----- %s", subg.name, subg.path)
                
            if work:
                logger.debug("CONNECTED: %s", node.anynode.dest.name)
            
            # Enter recursion if there is a subgroups
            if node.subgroups:
                self.walk_etree(subg, subhg)

    def rec_walk_tree(self, node):
        """ walk existing internal tree and for each group process the entries """
        # logger.debug("processing group: %s  ----- %s", node.name, node.path )
        if node.subgroups:
            logger.debug('node subgroups: %s', node.subgroups)
            if node.entries:
                # process all entries of current path
                logger.debug("enter work for middle entries in path %s", node.path)
                self.work_entries(node)
                pass
            for subg in node.subgroups:
                self.rec_walk_tree(subg)
        else:
            if node.path:
                logger.debug("enter work for lastlvl entries in path %s", node.path)
                self.work_entries(node)
                pass
            #for subg in node.subgroups:
            #    self.rec_walk_tree(subg)

    def rec_walk_tree_check(self, node):
        """ walk existing internal tree and for each group process the entries """
        # logger.debug("processing group: %s  ----- %s", node.name, node.path )
        if node.subgroups:
            if node.entries:
                # process all entries of current path
                logger.debug('check node.dest: %s', node.dest)
        else:
            if node.path:
                logger.debug('check node.dest: %s', node.dest)
            for subg in node.subgroups:
                self.rec_walk_tree_check(subg)

    def report(self):
        print("ERROR")
        pprint(self.results['err'])
        print()
        print("CRITICAL")
        pprint(self.results['crit'])
        print()
        print("count : ", self.count)
        print("count success: ", self.count_suc)
        print("count errors: ", self.count_err)
        print("count critical: ", self.count_crit)
    
