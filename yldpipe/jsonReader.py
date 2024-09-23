import logging
import json
from anytree import AnyNode, Node
from AbstractBase import AbstractReader
from utils import setup_logger

logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)


class JsonReader(AbstractReader):
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
        with open(file_path) as file:
            self.buffer[fn] = json.load(file)

    def read_all(self):
        for fn in self.cfg_si['out_fns']:
            self.read(fn)

    def get_buffer(self, fn):
        return self.buffer[fn]


class Tree: pass

from anytree.importer import JsonImporter
from anytree.search import find_by_attr
from anytree import RenderTree
importer = JsonImporter()

class JsonStorage:
    """ class for caching """

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def set_src(self, fp):
        self.fp = fp
        with open(fp) as file:
            self.fcontent = json.load(file)

    def _import(self):
        with open(self.fp) as file:
            fcontent = file.read()
            self.root = importer.import_(fcontent)
            # print(RenderTree(self.root))

    def find_groups_by_path(self, path):
        logger.debug('path: %s', path)
        val = path[0]
        res = find_by_attr(self.root_node, val, name='title', maxlevel=None)
        logger.debug('res: %s', res)
        return res

    def find_groups_by_path_OLD(self, path):
        logger.debug('path: %s', path)
        data = self.data
        # logger.debug('data: %s', data)
        #keys = path.split('/')
        keys = ['root'] + path
        logger.debug('keys: %s', keys)
        current = data
        for key in keys:
            if key in current:
                current = current[key]
            else:
                raise KeyError(f"Key '{key}' not found in the path '{path}'")
        return current

    def create_tree_from_json(self):  # root case
        json = self.fcontent
        root_node = Node("root")
        root_node.parent = None
        # cfg not avail in this class
        # self.attrs = self.cfg_kp_process_fields['kp_src_all_fields']
        self.attrs = list(json.keys())
        self.attrs.remove('children')
        self.attrs.remove('root')
        self._walk_tree(json, root_node)
        self.root_node = root_node
        self.tree = root_node

    # for firefox bookmark json, or json with children attribute
    def _walk_tree(self, json, node):  # recursive case
        # given json fragment is checked first if it has children
        # if yes, loop over the sub json fragments, create new Node and recurse
        # if not, it is a leaf node, and a new node is created
        #logger.debug('json-title: %s', json['title'])
        if 'children' in json.keys():
            for sub_json in json['children']:
                # logger.debug('sub_json-title: %s', sub_json['title'])
                child_node = Node(sub_json['title'], parent=node)
                # self.attr_copy(sub_json, child_node)
                [setattr(node, attr, sub_json[attr]) for attr in self.attrs]
                self._walk_tree(sub_json, child_node)
        else:
            pass
            # logger.debug('leaf-node: %s', json['title'])


    # unused currently
    def attr_copy(self, src, dst):
        """ copies attributes from a dict to an object """
        [setattr(dst, attr, src[attr]) for attr in self.attrs]

