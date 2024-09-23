
from anytree import NodeMixin, Node, AnyNode, RenderTree, PreOrderIter
import itertools

import logging
from utils import setup_logger
logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)

"""
class CustomNode(NodeMixin):
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

    def render(self, with_attr=False):
        for pre, fill, node in RenderTree(self):
            #print("%s%s" % (pre, node.name))
            if with_attr:
                if hasattr(node, 'dest'):   
                    print("%s%s-->%s" % (pre, node.id, node.dest.name))
                else:
                    print("%s%s" % (pre, node.id))
            else:
                print("%s%s" % (pre, node.id))
"""

class TreeSupport:
    def preOrderIter(self, root):
        for node in PreOrderIter(root):
            print(node.name)

    def create_new_anytree_rec_from_dict(self, yaml):
        """ create a tree from a yaml """
        # if root is given in data, use it, else create a root node
        root = Node('root')
        self.rec_yaml(yaml, root)
        self.root_node = root
        return root

    def render(self, **kwargs):
        print(kwargs)
        root = kwargs.get('root', None)
        if root:
            root.render(kwargs)
        else:
            self.root.render()

    def rec_yaml(self, data, node):
        """ recurse nested dict (ie from yaml) and add all content as tree descendants """
        logger.debug("enter recursion with node %s", node)

        if isinstance(data, dict):
            for key, item in data.items():
                child_node = Node(key, parent=node)
                self.rec_yaml(item, child_node)
        else:
            pass

