from AbstractBase import AbstractStorage
from anytree.search import find_by_attr
from anytree import RenderTree, Node, PreOrderIter
from anytree.exporter import DictExporter, JsonExporter
import yaml, json
from utils import setup_logger
import logging

logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)


class Tree: pass

class CustomNode(Node):
    """ node for firefox bookmarks json
    """
    _mypath = None
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        repr = '/'.join( [str(node.name) for node in self.path] )
        self.mypath = repr
        self.entries = []
        # logger.debug('self._path: %s', self._mypath)
    @property
    def mypath(self):
        return self._mypath
    @mypath.setter
    def mypath(self, val):
        self._mypath = val

    @property
    def subgroups(self):
        # if all children have no further kids
        sgroups = []
        for child in self.children:
            if child.typeCode == 2:
                sgroups.append(child)

        logger.debug('subgroups: %s', sgroups)
        return sgroups


class AnytreeStorage(AbstractStorage):
    """ class for anytree storage """

    # find by name and typeCode
    # find by mypath
    # etc. etc ? define use cases
    def find_groups_by_path(self, val, name='name', **kwargs):
        # in yaml cfg I need to avoid space in keys. So here replace it back
        #res = find_by_attr(self.root_node, val, name='title')
        #val = 'root/'+val
        res = find_by_attr(self.root_node, val, name=name, **kwargs)
        #res = find_by_attr(self.root_node, val, name='mypath', **kwargs)
        if res:
            out = res.name
        else:
            out = None
        # logger.debug('FIND: In %s val: %s - res: %s', self.__class__.__name__, val, out)
        return res

    def _import(self):
        self.root = self.importer.import_(self.yaml)
        logger.debug('self.root: %s', self.root)
        for node in self.root.children:
            logger.debug('node.title: %s', node.title)
        logger.debug('root children: %s', self.root.children)

    def export(self, fp, format='yaml'):

        if format == 'pure_hierarchy':
            data = {}
            for node in PreOrderIter(self.root_node):
                lg.debug('node: %s', node.name)
                # XXX
                # write yaml with identions bsaed on
            #attriter=lambda attrs: [(k, v) for k, v in attrs if k == "name"]
            exporter = DictExporter(attriter=lambda attrs: [(k, v) for k, v in attrs if k == "name"])
        if format == 'yaml':
            exporter = DictExporter()
            #exporter = DictExporter(attriter=lambda attrs: [(k, v) for k, v in attrs if k == "a"])
        if format == 'json':
            exporter = JsonExporter()
        blob = exporter.export(self.root_node)
        logger.debug('len(blob) %s, exporting as %s', len(blob), fp)
        with open(fp, 'w') as file:
            logger.debug('format: %s', format)
            if format in ['yaml', 'pure_hierarchy']:
                yaml.dump(blob, file)
            if format == 'json':
                json.dump(blob, file)


    def find_entry_by_path(self, path):
        pass

    def add_entry(self, group, row):
        node = self.find_groups_by_path(group.path)
        if node:
            if not hasattr(node, 'entries'):
                node.entries = []
            node.entries.append(row)
            logger.debug('node.entries: %s', node.entries)


    # unused currently
    def attr_copy(self, src, dst):
        """ copies attributes from a dict to an object """
        [setattr(dst, attr, src[attr]) for attr in self.attrs]

    def render(self):
        for pre, fill, node in RenderTree(self.root_node):
            print("%s%s" % (pre, node.name))

    def save(self):
        self.write()