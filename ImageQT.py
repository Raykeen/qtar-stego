from ImageQTNode import ImageQTNode
import numpy as np


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

    def image_with_qt_borders(self):
        image = np.copy(self.root_node.image)
        for leave in self.leaves:
            x0, y0, x1, y1 = leave.rect
            for x in range(x0, x1 - 1):
                image[x][y1 - 1] = 0

            for y in range(y0, y1 - 1):
                image[x1 - 1][y] = 0

        return image






