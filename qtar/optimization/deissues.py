import sys
from timeit import default_timer as timer
from math import sqrt, ceil
from copy import copy

from numpy import array

from qtar.core.qtar import QtarStego, DEFAULT_PARAMS
from qtar.optimization.metrics import bcr, psnr
from qtar.utils import classproperty


class OptIssueBase:
    desc = 'Base Issue\n' \
           'func: None\n' \
           'params: None'
    bounds = [(0, 1)]

    np = 1
    cr = 0.5
    f = 0.5
    evaluations = 2

    evaluations_done = 0
    time = None

    @classproperty
    def iter(cls):
        return ceil(cls.evaluations / (cls.np * len(cls.bounds)) - 1)

    @classproperty
    def max_evaluations(cls):
        return (cls.iter + 1) * cls.np * len(cls.bounds)

    @classmethod
    def func(cls, *args):
        return 0

    @classmethod
    def eval_callback(cls, callback, **kwargs):
        if cls.time is None:
            cls.time = timer()

        cls.evaluations_done += 1

        new_time = timer()
        callback(cls.evaluations_done, cls.max_evaluations, (new_time - cls.time) / cls.evaluations_done, **kwargs)


class OptIssue1(OptIssueBase):
    desc = 'Issue 1\n' \
           'func: -((psnr - def_psnr) / def_psnr + (bpp - def_bpp) / def_bpp)\n' \
           'params: threshold'
    bounds = [(0, 1)]

    np = 13
    cr = 0.7450
    f = 0.9096
    evaluations = 416

    @classmethod
    def func(cls, th, container, watermark, params, default_metrics, callback):
        def_psnr = default_metrics['container psnr']
        def_bpp = default_metrics['container bpp']
        params = copy(params)
        params['homogeneity_threshold'] = th[0]
        qtar = QtarStego.from_dict(params)

        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        container_image = embed_result.img_container
        stego_image = embed_result.img_stego
        psnr_ = psnr(container_image, stego_image)
        bpp_ = embed_result.bpp

        func = -((psnr_ - def_psnr) / def_psnr + (bpp_ - def_bpp) / def_bpp)

        if psnr_ < def_psnr or bpp_ < def_bpp:
            return func + 1000

        return func

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'homogeneity_threshold': def_params['homogeneity_threshold']
            }

        return {"homogeneity_threshold": result.x[0]}


class OptIssue2(OptIssueBase):
    desc = 'Issue 2\nfunc: BCR\nparams: threshold for 3 brightness levels'
    bounds = ((0, 1), (0, 1), (0, 1))

    np = 17
    cr = 0.7122
    f = 0.6301
    evaluations = 3111

    @classmethod
    def func(cls, threshold, container, watermark, params, default_metrics, callback):
        params = copy(params)
        params['homogeneity_threshold'] = threshold
        qtar = QtarStego.from_dict(params)
        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        watermark = embed_result.img_watermark
        extracted_wm = qtar.extract(embed_result.img_stego, embed_result.key)
        return -bcr(watermark, extracted_wm)

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'homogeneity_threshold': def_params['homogeneity_threshold']
            }

        return {"homogeneity_threshold": result.x}


class OptIssue3(OptIssueBase):
    desc = 'Issue 3\nfunc: PSNR\nparams: offset'
    bounds = ((0, 511), (0, 511))

    np = 10
    cr = 0.4862
    f = 1.1922
    evaluations = 820

    @classmethod
    def func(cls, offset, container, watermark, params, default_metrics, callback):
        params = copy(params)
        params['offset'] = array(offset).astype(int)
        qtar = QtarStego.from_dict(params)
        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        container_image = embed_result.img_container
        stego_image = embed_result.img_stego
        return -psnr(container_image, stego_image)

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'offset': def_params['offset']
            }

        return {'offset': array(result.x).astype(int)}


class OptIssue4(OptIssueBase):
    desc = 'Issue 4\nfunc: BCR\nParams: offset'
    bounds = ((0, 511), (0, 511))

    np = 10
    cr = 0.4862
    f = 1.1922
    evaluations = 820

    @classmethod
    def func(cls, offset, container, watermark, params, default_metrics, callback):
        params = copy(params)
        params['offset'] = array(offset).astype(int)
        qtar = QtarStego.from_dict(params)
        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        watermark = embed_result.img_watermark
        extracted_wm = qtar.extract(embed_result.img_stego, embed_result.key)
        return -bcr(watermark, extracted_wm)

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'offset': def_params['offset']
            }

        return {'offset': array(result.x).astype(int)}


class OptIssue5(OptIssueBase):
    desc = 'Issue 5\nfunc: PSNR\nparams: max bock size, quantization power, channel scale'
    bounds = ((3, 10), (0.01, 1), (1, 255))

    np = 17
    cr = 0.7122
    f = 0.6301
    evaluations = 3111

    @classmethod
    def func(cls, args, container, watermark, params, default_metrics, callback):
        max_b = 2 ** int(args[0])
        qp = args[1]
        sc = args[2]
        params = copy(params)
        params['max_block_size'] = max_b
        params['quant_power'] = qp
        params['ch_scale'] = sc
        qtar = QtarStego.from_dict(params)

        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        container_image = embed_result.img_container
        stego_image = embed_result.img_stego
        return -psnr(container_image, stego_image)

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'max_block_size': def_params['max_block_size'],
                'quant_power': def_params['quant_power'],
                'ch_scale': def_params['ch_scale']
            }

        return {
            'max_block_size': 2 ** int(result.x[0]),
            'quant_power': result.x[1],
            'ch_scale': result.x[2]
        }


class OptIssue6(OptIssueBase):
    desc = 'Issue 6\nFunc: BCR\nParams: max bock size, quantization power, channel scale'
    bounds = ((3, 10), (0.01, 1), (1, 255))

    np = 17
    cr = 0.7122
    f = 0.6301
    evaluations = 3111

    @classmethod
    def func(cls, args, container, watermark, params, default_metrics, callback):
        max_b = 2 ** int(args[0])
        qp = args[1]
        sc = args[2]
        params = copy(params)
        params['max_block_size'] = max_b
        params['quant_power'] = qp
        params['ch_scale'] = sc
        qtar = QtarStego.from_dict(params)
        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        watermark = embed_result.img_watermark
        extracted_wm = qtar.extract(embed_result.img_stego, embed_result.key)
        return -bcr(watermark, extracted_wm)

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'max_block_size': def_params['max_block_size'],
                'quant_power': def_params['quant_power'],
                'ch_scale': def_params['ch_scale']
            }
        return {
            'max_block_size': 2 ** int(result.x[0]),
            'quant_power': result.x[1],
            'ch_scale': result.x[2]
        }


class OptIssue7(OptIssueBase):
    desc = 'Issue 7\n' \
           'func: sqrt((-1 / psnr)^2 + (1 - bcr)^2 + (1 - bpp / maxbpp)^2)\n' \
           'params: threshold for 3 brightness levels, min bock size, max bock size, quantization power, channel scale'
    bounds = ((0, 1), (0, 1), (0, 1), (3, 10), (3, 10), (0.01, 1), (1, 255))

    np = 12
    cr = 0.2368
    f = 0.6702
    evaluations = 14028

    @classmethod
    def func(cls, args, container, watermark, params, default_metrics, callback):
        th = (args[0], args[1], args[2])
        max_b = 2 ** int(args[3])
        min_b = 2 ** int(args[4])
        if min_b > max_b:
            max_b = min_b
        qp = args[5]
        sc = args[6]
        params = copy(params)
        params['homogeneity_threshold'] = th
        params['min_block_size'] = min_b
        params['max_block_size'] = max_b
        params['quant_power'] = qp
        params['ch_scale'] = sc
        qtar = QtarStego.from_dict(params)

        maxbpp = len(container.getbands()) * 8
        try:
            embed_result = qtar.embed(container, watermark)
            container_image = embed_result.img_container
            stego_image = embed_result.img_stego
            watermark = embed_result.img_watermark
            extracted_wm = qtar.extract(stego_image, embed_result.key)

            cls.eval_callback(callback)

            psnr_ = psnr(container_image, stego_image)
            bcr_ = bcr(watermark, extracted_wm)
            bpp_ = embed_result.bpp
        except:
            return 1

        return sqrt((-1 / psnr_) ** 2 + (1 - bcr_) ** 2 + (1 - bpp_ / maxbpp) ** 2)

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'homogeneity_threshold': def_params['homogeneity_threshold'],
                'min_block_size': def_params['min_block_size'],
                'max_block_size': def_params['max_block_size'],
                'quant_power': def_params['quant_power'],
                'ch_scale': def_params['ch_scale']
            }

        max_b = 2 ** int(result.x[3])
        min_b = 2 ** int(result.x[4])
        if min_b > max_b:
            max_b = min_b

        return {
            'homogeneity_threshold': (result.x[0], result.x[1], result.x[2]),
            'min_block_size': min_b,
            'max_block_size': max_b,
            'quant_power': result.x[5],
            'ch_scale': result.x[6]
        }


class OptIssue8(OptIssueBase):
    desc = 'Issue 8\n' \
           'func: sqrt(psnr_w * (-1 / psnr)^2 + bcr_w * (1 - bcr)^2 + bpp_w * (1 - bpp / maxbpp)^2)\n' \
           'params: threshold for 3 brightness levels, quantization power, channel scale'
    bounds = ((0, 1), (0, 1), (0, 1), (0, 511), (0, 511), (0, 1), (1, 255))

    np = 12
    cr = 0.2368
    f = 0.6702
    evaluations = 14028

    @classmethod
    def func(cls, args, container, watermark, params, default_metrics, callback):
        th = (args[0], args[1], args[2])
        x = int(args[3])
        y = int(args[4])
        qp = args[5]
        sc = args[6]
        params = copy(params)
        params['homogeneity_threshold'] = th
        params['offset'] = (x, y)
        params['quant_power'] = qp
        params['ch_scale'] = sc
        qtar = QtarStego.from_dict(params)

        maxbpp = len(container.getbands()) * 8

        psnr_w = 0.999
        bcr_w = 0.0005
        bpp_w = 0.0005
        try:
            embed_result = qtar.embed(container, watermark)
            container_image = embed_result.img_container
            stego_image = embed_result.img_stego
            watermark = embed_result.img_watermark
            extracted_wm = qtar.extract(stego_image, embed_result.key)

            cls.eval_callback(callback)

            psnr_ = psnr(container_image, stego_image)
            bcr_ = bcr(watermark, extracted_wm)
            bpp_ = embed_result.bpp
        except:
            return 1

        return sqrt(psnr_w * (-1 / psnr_) ** 2 + bcr_w * (1 - bcr_) ** 2 + bpp_w * (1 - bpp_ / maxbpp) ** 2)

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'homogeneity_threshold': def_params['homogeneity_threshold'],
                'offset': def_params['offset'],
                'quant_power': def_params['quant_power'],
                'ch_scale': def_params['ch_scale']
            }
        return {
            'homogeneity_threshold': (result.x[0], result.x[1], result.x[2]),
            'offset': (int(result.x[3]), int(result.x[4])),
            'quant_power': result.x[5],
            'ch_scale': result.x[6]
        }


class OptIssue9(OptIssueBase):
    desc = 'Issue 9\n' \
           'func: -((psnr - def_psnr) / def_psnr + (bpp - def_bpp) / def_bpp)\n' \
           'params: threshold for 3 brightness levels, offset'
    bounds = ((0, 1), (0, 1), (0, 1), (0, 512), (0, 512))

    np = 12
    cr = 0.2368
    f = 0.6702
    evaluations = 10020

    @classmethod
    def func(cls, args, container, watermark, params, default_metrics, callback):
        def_psnr = default_metrics['container psnr']
        def_bpp = default_metrics['container bpp']
        th = (args[0], args[1], args[2])
        x = int(args[3])
        y = int(args[4])
        params = copy(params)
        params['homogeneity_threshold'] = th
        params['offset'] = (x, y)
        qtar = QtarStego.from_dict(params)

        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        container_image = embed_result.img_container
        stego_image = embed_result.img_stego
        psnr_ = psnr(container_image, stego_image)
        bpp_ = embed_result.bpp

        func = -((psnr_ - def_psnr) / def_psnr + (bpp_ - def_bpp) / def_bpp)

        if psnr_ < def_psnr or bpp_ < def_bpp:
            return func + 1000

        return func

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'homogeneity_threshold': def_params['homogeneity_threshold'],
                'offset': def_params['offset']
            }
        return {
            'homogeneity_threshold': (result.x[0], result.x[1], result.x[2]),
            'offset': (int(result.x[3]), int(result.x[4]))
        }


class OptIssue10(OptIssueBase):
    desc = 'Issue 10\n' \
           'func: -((psnr - def_psnr) / def_psnr + (bpp - def_bpp) / def_bpp)\n' \
           'params: threshold for 3 brightness levels'
    bounds = ((0, 1), (0, 1), (0, 1))

    np = 12
    cr = 0.2368
    f = 0.6702
    evaluations = 6012

    @classmethod
    def func(cls, args, container, watermark, params, default_metrics, callback):
        def_psnr = default_metrics['container psnr']
        def_bpp = default_metrics['container bpp']
        th = (args[0], args[1], args[2])
        params = copy(params)
        params['homogeneity_threshold'] = th
        qtar = QtarStego.from_dict(params)

        embed_result = qtar.embed(container, watermark)

        cls.eval_callback(callback)

        container_image = embed_result.img_container
        stego_image = embed_result.img_stego
        psnr_ = psnr(container_image, stego_image)
        bpp_ = embed_result.bpp

        func = -((psnr_ - def_psnr) / def_psnr + (bpp_ - def_bpp) / def_bpp)

        if psnr_ < def_psnr or bpp_ < def_bpp:
            return func + 1000

        return func

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'homogeneity_threshold': def_params['homogeneity_threshold']
            }
        return {
            'homogeneity_threshold': (result.x[0], result.x[1], result.x[2])
        }


class OptIssue11(OptIssueBase):
    desc = 'Issue 11\n' \
           'func: -((psnr_c - def_psnr_c) / def_psnr_c + (bpp - def_bpp) / def_bpp + (psnr_w - def_psnr_w) / def_psnr_w)\n' \
           'params: th1, th2, th3, cf, wm_b'
    bounds = ((0, 1), (0, 1), (0, 1), (0, 4), (0, 10))

    np = 20
    cr = 0.6938
    f = 0.9314
    evaluations = 10000

    @classmethod
    def func(cls, args, container, watermark, params, default_metrics, callback):
        def_psnr_c = default_metrics['container psnr']
        def_psnr_w = default_metrics['watermark psnr']
        def_bpp = default_metrics['container bpp']

        new_params = {
            'homogeneity_threshold': (args[0], args[1], args[2]),
            'cf_grid_size': 2 ** int(args[3]),
            'wmdct_block_size': 2 ** int(args[4])
        }

        params = copy(params)
        params.update(new_params)

        qtar = QtarStego.from_dict(params)

        try:
            embed_result = qtar.embed(container, watermark)
            wm_extracted = qtar.extract(embed_result.img_stego, embed_result.key)
        except Exception as e:
            cls.eval_callback(callback, error=e, new_params=new_params)
            return 0

        cls.eval_callback(callback)

        psnr_c = psnr(embed_result.img_container, embed_result.img_stego)
        psnr_w = psnr(embed_result.img_watermark, wm_extracted)
        bpp_ = embed_result.bpp

        func = -((psnr_c - def_psnr_c) / def_psnr_c + (bpp_ - def_bpp) / def_bpp + (psnr_w - def_psnr_w) / def_psnr_w)

        if psnr_c < def_psnr_c or bpp_ < def_bpp or psnr_w < def_psnr_w:
            return 0

        return func

    @staticmethod
    def get_new_params(result, def_params):
        if result.fun == 0:
            return {
                'homogeneity_threshold': def_params['homogeneity_threshold'],
                'cf_grid_size': def_params['cf_grid_size'],
                'wmdct_block_size': def_params['wmdct_block_size']
            }

        return {
            'homogeneity_threshold': (result.x[0], result.x[1], result.x[2]),
            'cf_grid_size': 2 ** int(result.x[3]),
            'wmdct_block_size': 2 ** int(result.x[4])
        }


ISSUES = [OptIssue1, OptIssue2, OptIssue3, OptIssue4, OptIssue5, OptIssue6, OptIssue7, OptIssue8, OptIssue9,
          OptIssue10, OptIssue11]
