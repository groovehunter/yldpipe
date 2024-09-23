class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

# Create source and destination trees
source_tree = Node("root")
n1 = Node("group1")
n1.children.append(Node("s1"))
n1.children.append(Node("s2"))
source_tree.children.append(n1)
source_tree.children.append(Node("group2"))
source_tree.children.append(Node("group3"))

destination_tree = Node("root")
d1 = Node("groupC")
d1.children.append(Node("ds1"))
d1.children.append(Node("ds2"))
destination_tree.children.append(d1)
destination_tree.children.append(Node("groupA"))
destination_tree.children.append(Node("groupB"))

# Define mapping dictionary
mappings = {
    "group1": "groupA",
    "group2": "groupB"
}

# Define recursive function to find and map node
def map_node(node, destination_tree, mappings):
    print(node.name)
    if node.name in mappings:
        # Find corresponding node in destination tree
        destination_node = next((child for child in destination_tree.children if child.name == mappings[node.name]), None)
        print("-- ", destination_node.name)
        if destination_node:
            # Map node to corresponding node in destination tree
            return destination_node
    else:
        print("NOT  node.name in mappings")
    for child in node.children:
        # Recursively search for and map child nodes
        print("check child ", child.name)
        mapped_child = map_node(child, destination_tree, mappings)
        if mapped_child:
            print("mapped child ", mapped_child.name)
            # Add mapped child to destination node
            if not 'destination_node' in globals():
                destination_node = destination_tree
            destination_node.children.append(mapped_child)
        else:
            print("mapped child = NONE")
    return None

# Call recursive function to map source tree to destination tree
mapped_node = map_node(source_tree, destination_tree, mappings)
