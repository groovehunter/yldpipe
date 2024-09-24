# from abc import abstractmethod
import yaml
from AbstractBase import AbstractReader
from anytreeStorage import AnytreeStorage, CustomNode
from anytree.importer import DictImporter
# from anytree import Node
# from treeSupport import TreeSupport

import logging
from utils import setup_logger

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


class YamlStorage(AnytreeStorage):
    """ class for yaml tree DB """
    importer = DictImporter()

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

    def create_tree_from_yaml(self, yaml, attrs):
        """ create a tree from a yaml """
        # if root is given in data, use it, else create a root node
        root = CustomNode('root')
        #root.mypath = 'root'
        self.attrs = attrs
        self.rec_yaml(yaml, root)
        self.root_node = root
        # self.render()
        # return root

    def rec_yaml(self, data, node):
        """ recurse nested dict (ie from yaml) and add all content as tree descendants """
        #logger.debug("enter recursion with node name %s, path=%s", node.name, node.mypath)
        #if data:
            #logger.debug('data: %s', data)
            # [ setattr(node, attr, data.get(attr, None)) for attr in self.attrs ]

        if isinstance(data, dict):
            for attr in self.attrs:
                setattr(node, attr, data.get(attr, None))
            for key, item in data.items():
                #logger.debug('key: %s, item: %s', key, item)
                child_node = CustomNode(key, parent=node)
                child_node.title = key
                # logger.debug('child_node: %s', child_node.name)
                self.rec_yaml(item, child_node)
        else:
            pass

    def find_groups_by_path(self, path):
        # logger.debug('path: %s', path)
        val = 'root/'+path
        kwargs = {}
        return super().find_groups_by_path(val, name='mypath', **kwargs)

    def find(self, key):
        for k, v in self.yaml.iteritems():
            logger.debug('k: %s, v: %s', k, v)
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in self.find(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in self.find(key, d):
                        yield result


    def find_entry_by_path(self, path):
        pass