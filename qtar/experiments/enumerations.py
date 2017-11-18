from copy import copy
from itertools import product
from collections import OrderedDict

import math
import pandas as pd
import numpy as np

from qtar.experiments.benchmark import embed
from qtar.utils import pick_values
from qtar.experiments import TEST_IMAGES_PATH, METRICS_NAMES, PARAMS_NAMES

pd.set_option('display.expand_frame_repr', False)


def enumerations(params):
    with open(params['experiments_path']) as file:
        images = [line.replace('\n', '').split(' ')[0:2] for line in file.readlines()]

    params_to_show = [params['param']]

    params_names = []

    for param_to_show in params_to_show:
        param_name = PARAMS_NAMES[param_to_show]

        if isinstance(param_name, (list, tuple)):
            params_names.extend(param_name)
        elif isinstance(params[param_to_show], (list, tuple)):
            params_names.extend([param_name + str(i) for i in range(len(params[param_to_show]))])
        else:
            params_names.append(param_name)

    metrics_to_show = 'container bpp', 'container psnr', 'container ssim', 'watermark psnr', 'watermark ssim', 'key size'
    metrics_names = pick_values(METRICS_NAMES, metrics_to_show)

    index_names = params_names
    headers = metrics_names

    index = pd.MultiIndex.from_tuples([], names=index_names)
    table = pd.DataFrame(columns=headers, index=index)

    for param_value in get_param_range(params):
        metics_sums = OrderedDict((metric, 0) for metric in metrics_to_show)

        for container_path, watermark_path in images:
            params = copy(params)
            params[params['param']] = param_value
            params['container'] = TEST_IMAGES_PATH + container_path
            params['watermark'] = TEST_IMAGES_PATH + watermark_path

            metrics = embed(params)
            for metric in metrics_to_show:
                metics_sums[metric] += metrics[metric]

        metrics_avg = OrderedDict((metric, metric_sum / len(images)) for metric, metric_sum in metics_sums.items())

        row_index = pd.MultiIndex.from_tuples([
            (param_value, )
        ], names=index_names)

        row = metrics_avg.values()

        result_row = pd.DataFrame([row], columns=headers, index=row_index)

        print(result_row)

        table = table.append(result_row)

    return table


def get_param_range(params):
    container_size = (512, 512)
    max_b = min(params['max_block_size'], min(container_size))
    min_b = params['min_block_size']
    param = params['param']

    return {
        'homogeneity_threshold': np.arange(0.01, 1.01, 0.01),
        'min_block_size': map(lambda x: 2**x, range(3, int(math.log2(max_b)) + 1)),
        'max_block_size': map(lambda x: 2**x, range(int(math.log2(min_b)), int(math.log2(max_b)) + 1)),
        'quant_power': np.arange(0.1, 1, 0.01),
        'cf_grid_size': map(lambda x: 2**x, range(0, int(math.log2(min_b)) + 1)),
        'ch_scale': np.arange(0.1, 20, 0.1),
        'offset': product(range(0, container_size[0], 1), range(0, container_size[1])),
        'wmdct_scale': np.arange(0.01, 1.01, 0.01),
        'wmdct_block_size': map(lambda x: 2**x, range(3, 10))
    }[param]
