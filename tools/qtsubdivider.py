import matplotlib.pyplot as plt
import numpy as np
from qtar.core.matrixregion import MatrixRegions, draw_borders

size = 16
mx = np.zeros(size ** 2).reshape((size, size))
rects = [(0, 0, size, size)]

mr = MatrixRegions(rects, mx)
imgplot = plt.imshow(draw_borders(mr, 255, True))

ann_list = []


def onclick(event):
    x = event.xdata
    y = event.ydata

    new_rects = []

    for ann in ann_list:
        ann.remove()

    ann_list[:] = []

    for x0, y0, x1, y1 in mr.rects:
        if x0 <= x < x1 and y0 <= y < y1:
            width = int((x1 - x0) / 2)
            height = int((y1 - y0) / 2)
            new_rects.append((x0, y0, x0 + width, y0 + height))
            new_rects.append((x0 + width, y0, x1, y0 + height))
            new_rects.append((x0, y0 + height, x0 + width, y1))
            new_rects.append((x0 + width, y0 + height, x1, y1))
        else:
            new_rects.append((x0, y0, x1, y1))

    mr.rects = new_rects

    print(new_rects)

    for i, rect in enumerate(mr.rects):
        x0, y0, x1, y1 = rect
        ann = plt.annotate("%d" % i, xy=(x0, y0), color='yellow')
        ann_list.append(ann)

    imgplot.set_data(draw_borders(mr, 255, True))
    plt.draw()


imgplot.figure.canvas.mpl_connect("button_press_event", onclick)
plt.show()
