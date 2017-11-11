from copy import copy
from collections import OrderedDict

import pandas as pd
from scipy.optimize import minimize_scalar

from qtar.experiments.benchmark import embed
from qtar.utils import extract_filename, pick
from qtar.experiments import TEST_IMAGES_PATH

pd.set_option('display.expand_frame_repr', False)

METRICS_NAMES = "container bpp", "container psnr", "container ssim", "watermark psnr", "watermark ssim"


def qtar_vs_cf_qtar(params):
    with open(params['experiments_path']) as file:
        images = [line.replace('\n', '').split(' ')[0:2] for line in file.readlines()]

    index_names = ['alg', 'container', 'watermark']
    headers = ('q',
               'capacity, BPP',
               'container PSNR, dB',
               'container SSIM, db',
               'secret img PSNR, dB',
               'secret img SSIM, db')

    index = pd.MultiIndex.from_tuples([], names=index_names)
    table = pd.DataFrame(columns=headers, index=index)

    for container_path, watermark_path in images:
        params = copy(params)
        params['container'] = TEST_IMAGES_PATH + container_path
        params['watermark'] = TEST_IMAGES_PATH + watermark_path

        qtar_params = copy(params)
        qtar_params['cf_grid_size'] = False

        cfqtar_params = copy(params)
        if params['cf_grid_size']:
            cfqtar_params['cf_grid_size'] = params['cf_grid_size']
        else:
            cfqtar_params['cf_grid_size'] = 8

        qtar_metrics = embed(qtar_params)

        cfqtar_params['quant_power'] = find_q_for_capacity(cfqtar_params, qtar_metrics['container bpp'])

        qtar_metrics = pick(qtar_metrics, METRICS_NAMES).values()

        cfqtar_metrics = embed(cfqtar_params)
        cfqtar_metrics = pick(cfqtar_metrics, METRICS_NAMES).values()

        growth = [cf/qt - 1 for qt, cf in zip(qtar_metrics, cfqtar_metrics)]

        container_file_name = extract_filename(container_path)
        watermark_file_name = extract_filename(watermark_path)

        row_index = pd.MultiIndex.from_tuples([
            ('QTAR', container_file_name, watermark_file_name),
            ('CF-QTAR', container_file_name, watermark_file_name),
            ('Прирост', container_file_name, watermark_file_name)
        ], names=index_names)

        qtar_row = (qtar_params['quant_power'], *qtar_metrics)
        cfqtar_row = (cfqtar_params['quant_power'], *cfqtar_metrics)

        result_row = pd.DataFrame([qtar_row, cfqtar_row, ('', *growth)], columns=headers, index=row_index)

        print(result_row)

        table = table.append(result_row)

    return table


def find_q_for_capacity(params, target_bpp):
    def f(q):
        p = copy(params)
        p['quant_power'] = q

        try:
            bpp = embed(p)['container bpp']
        except:
            return 10

        res = abs(target_bpp - bpp)

        if target_bpp > bpp:
            res = res * 3

        return res

    result = minimize_scalar(f, bracket=(0, 1, 2), method='golden', tol=0.001)
    return result.x


