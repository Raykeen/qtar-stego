from copy import copy

import pandas as pd

from qtar.experiments.benchmark import embed
from qtar.utils import extract_filename, pick_values, flatten
from qtar.experiments import TEST_IMAGES_PATH, METRICS_NAMES, PARAMS_NAMES

pd.set_option('display.expand_frame_repr', False)


def efficiency(params):
    with open(params['experiments_path']) as file:
        images = [line.replace('\n', '').split(' ')[0:2] for line in file.readlines()]

    params_to_show = ['homogeneity_threshold',
                      'min_block_size',
                      'max_block_size',
                      'quant_power',
                      'ch_scale',
                      'offset']

    if params['cf_mode']:
        params_to_show.append('cf_grid_size')
    if params['wmdct_mode']:
        params_to_show.append('wmdct_block_size')
        params_to_show.append('wmdct_scale')

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

    index_names = ['Контейнер', 'Секретное изображение']
    headers = params_names + metrics_names

    index = pd.MultiIndex.from_tuples([], names=index_names)
    table = pd.DataFrame(columns=headers, index=index)

    for container_path, watermark_path in images:
        params = copy(params)
        params['container'] = TEST_IMAGES_PATH + container_path
        params['watermark'] = TEST_IMAGES_PATH + watermark_path

        metrics = embed(params)
        metrics = flatten(pick_values(metrics, metrics_to_show))

        container_file_name = extract_filename(container_path)
        watermark_file_name = extract_filename(watermark_path)

        row_index = pd.MultiIndex.from_tuples([
            (container_file_name, watermark_file_name)
        ], names=index_names)

        params_values = flatten(pick_values(params, params_to_show))

        row = params_values + metrics

        result_row = pd.DataFrame([row], columns=headers, index=row_index)

        print(result_row)

        table = table.append(result_row)

    return table

