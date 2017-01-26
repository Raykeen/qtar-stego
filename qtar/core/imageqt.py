from qtar.core.matrixregion import *


class QtNode:
    ROOT = 0
    BRANCH = 1
    LEAF = 2

    def __init__(self, parent, rect=None):
        self.parent = parent
        self.children = [None, None, None, None]
        self.rect = rect
        x0, y0, x1, y1 = self.rect
        self.size = x1-x0
        if not parent:
            self.depth = 0
        else:
            self.depth = parent.depth + 1

        if not self.parent:
            self.type = QtNode.ROOT
        else:
            self.type = QtNode.LEAF

    def subdivide(self):
        x0, y0, x1, y1 = self.rect

        h = int((x1 - x0) / 2)
        rects = list()
        rects.append((x0, y0, x0 + h, y0 + h))
        rects.append((x0 + h, y0, x1, y0 + h))
        rects.append((x0, y0 + h, x0 + h, y1))
        rects.append((x0 + h, y0 + h, x1, y1))
        self.type = QtNode.BRANCH
        for n in range(len(rects)):
            self.children[n] = QtNode(self, rects[n])

        return self.children


class ImageQT(MatrixRegions):
    def __init__(self, matrix, min_size, max_size, threshold):
        super().__init__([], matrix)
        self.threshold = threshold
        self.min_size = min_size
        self.max_size = max_size
        self.max_depth = 0
        self.all_nodes = []
        self.leaves = []
        self.build_tree(QtNode(None, (0, 0, matrix.shape[1], matrix.shape[0])))
        self.rects = [leave.rect for leave in self.leaves]

    def build_tree(self, node):
        too_big = node.size > self.max_size
        too_small = node.size <= self.min_size
        self.all_nodes.append(node)

        if (not too_big and self.spans_homogeneity(node.rect)) or too_small:
            if node.depth > self.max_depth:
                self.max_depth = node.depth
            self.leaves.append(node)
            return

        children = node.subdivide()
        for child in children:
            self.build_tree(child)

    def spans_homogeneity(self, rect):
        region = self.get_region(rect)
        max_value = np.amax(region)
        min_value = np.amin(region)
        homogeneity = max_value - min_value
        if isinstance(self.threshold, (float, int)):
            return homogeneity < self.threshold * 256
        else:
            brightness = np.average(region)
            bright_types_count = len(self.threshold)
            for i in range(0, bright_types_count-1):
                bright_type_max = (int(255 / bright_types_count * (i + 1)))
                if brightness <= bright_type_max:
                    return homogeneity < self.threshold[i] * 256
            return homogeneity < self.threshold[-1] * 256



