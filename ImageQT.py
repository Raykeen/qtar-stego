from ImageQTNode import ImageQTNode


class ImageQT:
    def __init__(self, rootnode):
        rootnode.subdivide()  # constructs the network of nodes
        self.all_nodes = []
        self.leaves = []
        self.max_depth = 0
        self.prune(rootnode)
        self.traverse(rootnode)

    def prune(self, node):
        if node.type == ImageQTNode.LEAF:
            return
        if not node.children[0]:
            node.type = ImageQTNode.LEAF
            return

        for child in node.children:
            self.prune(child)

    def traverse(self, node):
        self.all_nodes.append(node)
        if node.type == ImageQTNode.LEAF:
            self.leaves.append(node)
            if node.depth > self.max_depth:
                self.max_depth = node.depth
        for child in node.children:
            if child:
                self.traverse(child)  # << recursion
