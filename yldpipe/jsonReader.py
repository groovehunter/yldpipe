import logging
import json
from anytree import AnyNode, Node, RenderTree
from AbstractBase import AbstractReader
from anytree.importer import JsonImporter
from utils import setup_logger
from anytreeStorage import AnytreeStorage, CustomNode

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

class Entry:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def __repr__(self):
        return "Entry: "+self.title


class JsonStorage(AnytreeStorage):
    """ class for caching """
    importer = JsonImporter()

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def set_src(self, fp):
        self.fp = fp
        with open(fp) as file:
            self.fcontent = json.load(file)

    def _import(self):
        self.root = self.importer.import_(self.fcontent)
        # print(RenderTree(self.root))

    def create_tree_from_json(self, attrs):  # root case
        json = self.fcontent

        root_node = CustomNode("root")
        root_node.parent = None
        root_node.uri = None
        # cfg not avail in this class
        #self.attrs = list(json.keys())
        self.attrs = attrs  # ['title', 'uri']
        # logger.debug('attrs: %s', self.attrs)
        self._walk_tree(json, root_node)
        self.root_node = root_node
        self.tree = root_node
        self.render()

    # for firefox bookmark json, or json with children attribute
    def _walk_tree(self, json, node):  # recursive case
        # given json fragment is checked first if it has children
        # if yes, loop over the sub json fragments, create new CustomNode and recurse
        # if not, it is a leaf node, and a new node is created
        [ setattr(node, attr, json.get(attr, None)) for attr in self.attrs ]
        #logger.debug('json-title: %s', json['title'])
        if 'children' in json.keys():
            for sub_json in json['children']:
                if sub_json['typeCode'] == 2:
                    # logger.debug('typeCode, title: %s, %s', sub_json['typeCode'], sub_json['title'])
                    child_node = CustomNode(sub_json['title'], parent=node)
                    self._walk_tree(sub_json, child_node)
                """
                if sub_json['typeCode'] == 1:
                    entry = self.create_entry(sub_json)
                    node.entries.append(entry)
                """
        else:
            pass
            # logger.debug('leaf-node: %s', json['title'])

    def create_entry(self, json):
        entry = Entry(**json)
        return entry

    def find_groups_by_path(self, path):
        path = 'root/'+path
        val = path.replace('_', ' ')
        #kwargs = {'typeCode': 2}
        kwargs = {}
        return super().find_groups_by_path(val, name='mypath', **kwargs)
