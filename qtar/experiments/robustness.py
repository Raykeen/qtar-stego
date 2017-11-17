from copy import copy

import pandas as pd

from qtar.experiments.benchmark import embed
from qtar.utils import extract_filename, pick_values, flatten
from qtar.experiments import TEST_IMAGES_PATH, METRICS_NAMES
from qtar.experiments.filters import filters

pd.set_option('display.expand_frame_repr', False)

PATHS_TO_RESULT_IMAGES = 'experiments\\robustness'


def robustness(params):
    with open(params['experiments_path']) as file:
        images = [line.replace('\n', '').split(' ')[0:2] for line in file.readlines()]

    metrics_to_show = 'watermark psnr', 'watermark ssim'
    metrics_names = pick_values(METRICS_NAMES, metrics_to_show)

    index_names = ['Контейнер', 'Секретное изображение', 'Фильтр']
    headers = metrics_names

    index = pd.MultiIndex.from_tuples([], names=index_names)
    table = pd.DataFrame(columns=headers, index=index)

    for container_path, watermark_path in images:
        params = copy(params)
        params['container'] = TEST_IMAGES_PATH + container_path
        params['watermark'] = TEST_IMAGES_PATH + watermark_path

        container_file_name = extract_filename(container_path)
        watermark_file_name = extract_filename(watermark_path)

        for filter_name, filter_ in filters:
            result = embed(params, filter_)
            metrics = flatten(pick_values(result, metrics_to_show))

            result['stego img'].save('%s\\%s in %s stego %s.bmp' %
                                     (PATHS_TO_RESULT_IMAGES, watermark_file_name, container_file_name, filter_name))
            result['extracted wm'].save('%s\\%s in %s wm %s.bmp' %
                                     (PATHS_TO_RESULT_IMAGES, watermark_file_name, container_file_name, filter_name))

            row_index = pd.MultiIndex.from_tuples([
                (container_file_name, watermark_file_name, filter_name)
            ], names=index_names)

            row = metrics

            result_row = pd.DataFrame([row], columns=headers, index=row_index)

            print(result_row)

            table = table.append(result_row)

    return table

