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

    @property
    def title(self):
        if hasattr(self, 'name'):
            return self.name
        return self.title
    @title.setter
    def title(self, val):
        self.name = val

class AnytreeStorage(AbstractStorage):
    """ class for anytree storage """
    root_node = None
    use_default_group = False

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
            if self.use_default_group:
                res = self.root_node
                out = res.name
        logger.debug('FIND: In %s val: %s - res: %s', self.__class__.__name__, val, out)
        return res

    def load_hierarchy(self, path):
        pass

    def load_hierarchy_from_yaml(self, fp):
        with open(fp) as file:
            self.yaml = yaml.load(file, Loader=yaml.FullLoader)


    def _import(self):
        self.root = self.importer.import_(self.yaml)
        logger.debug('self.root: %s', self.root)
        for node in self.root.children:
            logger.debug('node.title: %s', node.title)
        logger.debug('root children: %s', self.root.children)


    def prepare_export(self, fp, format='yaml'):
        pass

    def export(self, fp, format='yaml'):
        self.prepare_export(fp, format=format)

        if format == 'pure_hierarchy':
            data = {}
            for node in PreOrderIter(self.root_node):
                pass
                # logger.debug('node: %s', node.name)
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
            # logger.debug('node.entries: %s', node.entries)


    # unused currently
    def attr_copy(self, src, dst):
        """ copies attributes from a dict to an object """
        [setattr(dst, attr, src[attr]) for attr in self.attrs]

    def render(self):
        for pre, fill, node in RenderTree(self.root_node):
            print("%s%s" % (pre, node.name))

    def save(self):
        self.write()

    def write(self):
        pass

    def create_tree_from_json(self, attrs):
        pass

    def create_tree_from_yaml(self, attrs):
        """ create a tree from a yaml """
        # if root is given in data, use it, else create a root node
        #root.mypath = 'root'
        self.attrs = attrs
        self.rec_yaml(yaml, self.root_node)
        # self.render()

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

    def create_tree_from_kdbx(self):
        pass