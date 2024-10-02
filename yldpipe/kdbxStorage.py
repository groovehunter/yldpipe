import os.path
from shutil import copyfile
from anytreeStorage import AnytreeStorage
import logging
import itertools
from utils import setup_logger
from yldpipe.anytreeStorage import CustomNode

logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
from pykeepass import PyKeePass
from creds import db_path, pw

class keepassNode(CustomNode):
    # subnodes in anytree are called children
    # entries is something different, a item of content
    """
    @property
    def children(self):
        return self.entries
    @children.setter
    def children(self, val):
        self.entries = val
    """


class KdbxStorage(AnytreeStorage, PyKeePass):

    def __init__(self):
        AnytreeStorage.__init__(self)

    def set_src(self, db_path):
        logger.debug('db_path: %s', db_path)
        if not os.path.exists(db_path):
            logger.error('file not found: %s', db_path)
            db_path_empty = self.cfg_si['data_out_path'].joinpath(self.cfg_si['db_file_empty'])
            db_path_dst   = self.cfg_si['data_out_path'].joinpath(self.cfg_si['db_file_dst'])
            copyfile(db_path_empty, db_path_dst)
            logger.debug('copied empty db to: %s', db_path_dst)

        password = pw
        if self.cfg_si.get('pw') is not None:
            password = self.cfg_si['pw']
        PyKeePass.__init__(self, filename=db_path, password=password)
        #self.data = PyKeePass(filename=fp, password=pw)

    def create_tree_from_kdbx(self):
        self.root_node = keepassNode('root')
        self.root_node.entries = []
        self._rec_tree(self.root_node, self.root_group)
        self.render()

    def _rec_tree(self, node, group):
        if group.subgroups == []:
            return
        else:
            #logger.debug('node: %s', node.children)
            for subgroup in group.subgroups:
                subnode = keepassNode(subgroup.name)
                subnode.entries = subgroup.entries
                temp = list(itertools.chain(node.children, [subnode]))
                node.children = temp
                self._rec_tree(subnode, subgroup)

    """
    def prepare_export_from_anytree(self, fp, format='yaml'):
        self.create_tree_from_yaml(self.data)

    def prepare_export(self, fp, format='yaml'):
        # walk pykeepass tree and prepare for export 
        logger.debug('self.root_group: %s', self.root_group)
        self.data = self._rec_groups(self.root_group) #, data)
        logger.debug('self.data: %s', self.data)

    def _rec_groups(self, node): #, data):
        data = {}
        if True:
            for subgroup in node.subgroups:
                #data.append( { node.name: res } )
                data[subgroup.name] = self._rec_groups(subgroup)  # , data)
            return data
    """

    def find_groups_by_path(self, path, **kwargs):
        logger.debug('path: %s', path)
        res = PyKeePass.find_groups_by_path(self, [path])
        #logger.debug('res: %s', res)
        return res