import logging
from abc import abstractmethod

import yaml
from AbstractBase import AbstractReader, AbstractStorage
from utils import setup_logger
from anytree import AnyNode
from treeSupport import TreeSupport


logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)


class YamlReader(AbstractReader):
    """ access a set of files as input """
    cfg_si = {}
    reader = {}

    def __init__(self):
        self.buffer = {}

    def init_reader(self):
        logger.debug('opening file %s', self.fn_in)
        pass

    def get_fieldnames(self, fn=None):
        """ read first sheet and return col names """
        if not fn: fn = self.cfg_si['out_fns'][0]
        self.fieldnames = list(self.buffer[fn])
        return self.fieldnames

    def read(self, fn):
        file_path = data_in.joinpath(fn + '.yml')
        self.buffer[fn] = yaml.load(file_path, Loader=yaml.FullLoader)

    def read_all(self):
        for fn in self.cfg_si['out_fns']:
            self.read(fn)

    def get_buffer(self, fn):
        return self.buffer[fn]

from anytree.importer import DictImporter
importer = DictImporter()

# XXX inherit from NodeMixin or own TreeSupport
class YamlStorage(AbstractStorage, TreeSupport):
    """ class for yaml tree DB """

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def set_src(self, fp):
        self.fp = fp

    def write(self):
        with open(self.fp, 'w') as file:
            yaml.dump(self.data, file)

    def load_hierarchy_from_yaml(self, fp):
        with open(fp) as file:
            self.yaml = yaml.load(file, Loader=yaml.FullLoader)

    def _import(self):
        self.root = importer.import_(self.yaml)
        logger.debug('self.root: %s', self.root)
        for node in self.root.children:
            logger.debug('node.title: %s', node.title)
        logger.debug('root children: %s', self.root.children)

    def create_tree_from_yaml(self, data):
        self.create_new_anytree_rec_from_dict(data)

    def find(self, key):
        for k, v in self.yaml.iteritems():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in find(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find(key, d):
                        yield result

    def find_groups_by_path(self, path):
        last = path[-1]
        self.find(last)
        """
        logger.debug('path: %s', path)
        data = self.data
        logger.debug('data: %s', data)
        #keys = path.split('/')
        keys = ['root'] + path
        logger.debug('keys: %s', keys)
        current = data
        found = False
        while not found:
            if key in current:
                current = current[key]
            else:
                raise KeyError(f"Key '{key}' not found in the path '{path}'")
        return current
        """

    def find_entry_by_path(self, path):
        pass