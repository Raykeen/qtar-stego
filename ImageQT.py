from ImageQTNode import *


class ImageQT:
    def __init__(self, root_node):
        root_node.subdivide()  # constructs the network of nodes
        self.root_node = root_node
        self.all_nodes = []
        self.leaves = []
        self.max_depth = 0
        self._prune(root_node)
        self._traverse(root_node)

    def _prune(self, node):
        if node.type == ImageQTNode.LEAF:
            return
        if not node.children[0]:
            node.type = ImageQTNode.LEAF
            return

        for child in node.children:
            self._prune(child)

    def _traverse(self, node):
        self.all_nodes.append(node)
        if node.type == ImageQTNode.LEAF:
            self.leaves.append(node)
            if node.depth > self.max_depth:
                self.max_depth = node.depth
        for child in node.children:
            if child:
                self._traverse(child)  # << recursion
