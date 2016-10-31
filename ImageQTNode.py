import numpy as np


class ImageQTNode:
    ROOT = 0
    BRANCH = 1
    LEAF = 2

    def __init__(self, parent, rect, image, threshold, min_size, max_size):
        self.parent = parent
        self.rect = rect
        x0, y0, x1, y1 = rect
        self.size = x1 - x0
        self.image = image
        self.threshold = threshold
        self.min_size = min_size
        self.max_size = max_size
        self.children = [None, None, None, None]
        if not parent:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
        if not self.parent:
            self.type = ImageQTNode.ROOT
        else:
            self.type = ImageQTNode.BRANCH

    def subdivide(self):
        too_big = self.size > self.max_size
        too_small = self.size <= self.min_size
        if (not too_big and self.spans_homogeneity(self.rect)) or too_small:
            self.type = ImageQTNode.LEAF
            return

        x0, z0, x1, z1 = self.rect
        h = int((x1 - x0) / 2)
        rects = list()
        rects.append((x0, z0, x0 + h, z0 + h))
        rects.append((x0, z0 + h, x0 + h, z1))
        rects.append((x0 + h, z0 + h, x1, z1))
        rects.append((x0 + h, z0, x1, z0 + h))
        for n in range(len(rects)):
            self.children[n] = self.getinstance(rects[n])
            self.children[n].subdivide()  # << recursion

    def getinstance(self, rect):
        return ImageQTNode(self, rect, self.image, self.threshold, self.min_size, self.max_size)

    def spans_homogeneity(self, rect):
        x0, y0, x1, y1 = rect
        region = self.image[x0:x1, y0:y1]
        max_value = np.amax(region)
        min_value = np.amin(region)
        homogeneity = max_value - min_value
        return homogeneity < self.threshold
