from copy import copy
from collections import OrderedDict

import pandas as pd
from scipy.optimize import minimize_scalar

from qtar.experiments.benchmark import embed
from qtar.utils import extract_filename, pick
from qtar.experiments import TEST_IMAGES_PATH

pd.set_option('display.expand_frame_repr', False)

METRICS_NAMES = "container bpp", "container psnr", "container ssim", "watermark psnr", "watermark ssim"


def cfqtar_vs_decfqtarpmwdct(params):
    with open(params['experiments_path']) as file:
        images = [line.replace('\n', '').split(' ')[0:8] for line in file.readlines()]

    index_names = ['container', 'watermark', 'alg']
    headers = ('q',
               'capacity, BPP',
               'container PSNR, dB',
               'container SSIM, db',
               'secret img PSNR, dB',
               'secret img SSIM, db')

    index = pd.MultiIndex.from_tuples([], names=index_names)
    table = pd.DataFrame(columns=headers, index=index)

    for container_path, watermark_path, th1, th2, th3, min_b, cf_g, wmdct_b in images:
        params = copy(params)
        params['container'] = TEST_IMAGES_PATH + container_path
        params['watermark'] = TEST_IMAGES_PATH + watermark_path

        cfqtar_params = copy(params)
        cfqtar_params['cf_mode'] = True
        cfqtar_params['cf_grid_size'] = 8
        cfqtar_params['min_block_size'] = 16

        cfqtarpmwdct_params = copy(params)
        cfqtarpmwdct_params['cf_mode'] = True
        cfqtarpmwdct_params['pm_mode'] = True
        cfqtarpmwdct_params['wmdct_mode'] = True
        cfqtarpmwdct_params['homogeneity_threshold'] = [float(th) for th in [th1, th2, th3]]
        cfqtarpmwdct_params['min_block_size'] = int(min_b)
        cfqtarpmwdct_params['cf_grid_size'] = int(cf_g)
        cfqtarpmwdct_params['wmdct_block_size'] = int(wmdct_b)
        cfqtarpmwdct_params['wmdct_scale'] = 0.1

        cfqtar_metrics = embed(cfqtar_params)

        cfqtarpmwdct_params['quant_power'] = find_q_for_capacity(cfqtarpmwdct_params, cfqtar_metrics['container bpp'])

        cfqtar_metrics = pick(cfqtar_metrics, METRICS_NAMES).values()

        cfqtarpmwdct_metrics = embed(cfqtarpmwdct_params)
        cfqtarpmwdct_metrics = pick(cfqtarpmwdct_metrics, METRICS_NAMES).values()

        growth = [cfqtarpmwdct/cfqtar - 1 for cfqtar, cfqtarpmwdct in zip(cfqtar_metrics, cfqtarpmwdct_metrics)]

        container_file_name = extract_filename(container_path)
        watermark_file_name = extract_filename(watermark_path)

        row_index = pd.MultiIndex.from_tuples([
            (container_file_name, watermark_file_name, 'CF-QTAR'),
            (container_file_name, watermark_file_name, 'CF-QTAR PM SIDCT'),
            (container_file_name, watermark_file_name, 'Прирост')
        ], names=index_names)

        cfqtar_row = (cfqtar_params['quant_power'], *cfqtar_metrics)
        cfqtarpmwdct_row = (cfqtarpmwdct_params['quant_power'], *cfqtarpmwdct_metrics)

        result_row = pd.DataFrame([cfqtar_row, cfqtarpmwdct_row, ('', *growth)], columns=headers, index=row_index)

        print(result_row)

        table = table.append(result_row)

    return table


def qtar_vs_decfqtarpmwdct(params):
    with open(params['experiments_path']) as file:
        images = [line.replace('\n', '').split(' ')[0:8] for line in file.readlines()]

    index_names = ['container', 'watermark', 'alg']
    headers = ('q',
               'capacity, BPP',
               'container PSNR, dB',
               'container SSIM, db',
               'secret img PSNR, dB',
               'secret img SSIM, db')

    index = pd.MultiIndex.from_tuples([], names=index_names)
    table = pd.DataFrame(columns=headers, index=index)

    for container_path, watermark_path, th1, th2, th3, min_b, cf_g, wmdct_b in images:
        params = copy(params)
        params['container'] = TEST_IMAGES_PATH + container_path
        params['watermark'] = TEST_IMAGES_PATH + watermark_path

        qtar_params = copy(params)
        qtar_params['cf_mode'] = False
        qtar_params['cf_grid_size'] = False

        cfqtarpmwdct_params = copy(params)
        cfqtarpmwdct_params['cf_mode'] = True
        cfqtarpmwdct_params['pm_mode'] = True
        cfqtarpmwdct_params['wmdct_mode'] = True
        cfqtarpmwdct_params['homogeneity_threshold'] = [float(th) for th in [th1, th2, th3]]
        cfqtarpmwdct_params['min_block_size'] = int(min_b)
        cfqtarpmwdct_params['cf_grid_size'] = int(cf_g)
        cfqtarpmwdct_params['wmdct_block_size'] = int(wmdct_b)

        qtar_metrics = embed(qtar_params)

        cfqtarpmwdct_params['quant_power'] = find_q_for_capacity(cfqtarpmwdct_params, qtar_metrics['container bpp'])

        qtar_metrics = pick(qtar_metrics, METRICS_NAMES).values()

        cfqtar_metrics = embed(cfqtarpmwdct_params)
        cfqtar_metrics = pick(cfqtar_metrics, METRICS_NAMES).values()

        growth = [cf/qt - 1 for qt, cf in zip(qtar_metrics, cfqtar_metrics)]

        container_file_name = extract_filename(container_path)
        watermark_file_name = extract_filename(watermark_path)

        row_index = pd.MultiIndex.from_tuples([
            (container_file_name, watermark_file_name, 'QTAR'),
            (container_file_name, watermark_file_name, 'CF-QTAR PM SIDCT'),
            (container_file_name, watermark_file_name, 'Прирост')
        ], names=index_names)

        qtar_row = (qtar_params['quant_power'], *qtar_metrics)
        cfqtar_row = (cfqtarpmwdct_params['quant_power'], *cfqtar_metrics)

        result_row = pd.DataFrame([qtar_row, cfqtar_row, ('', *growth)], columns=headers, index=row_index)

        print(result_row)

        table = table.append(result_row)

    return table


def qtar_vs_cf_qtar(params):
    with open(params['experiments_path']) as file:
        images = [line.replace('\n', '').split(' ')[0:2] for line in file.readlines()]

    index_names = ['container', 'watermark', 'alg']
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
        qtar_params['cf_mode'] = False
        qtar_params['cf_grid_size'] = False

        cfqtar_params = copy(params)
        cfqtar_params['cf_mode'] = True
        cfqtar_params['min_block_size'] = 16
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
            (container_file_name, watermark_file_name, 'QTAR'),
            (container_file_name, watermark_file_name, 'CF-QTAR'),
            (container_file_name, watermark_file_name, 'Прирост')
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
        except Exception as e:
            print(e)
            return 10

        res = abs(target_bpp - bpp)

        if target_bpp > bpp:
            res = res * 3

        return res

    result = minimize_scalar(f, bounds=(0, 2), method='bounded', tol=0.001)
    return result.x


