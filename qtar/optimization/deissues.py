from timeit import default_timer as timer
from math import sqrt
from copy import copy

from numpy import array

from qtar.core.qtar import QtarStego, DEFAULT_PARAMS
from qtar.optimization.metrics import bcr, psnr


class OptIssueBase:
    desc = 'Base Issue\n' \
           'func: None\n' \
           'params: None'
    bounds = []

    np = 1
    cr = 0.5
    f = 0.5
    iter = 1

    evaluations = 0
    time = None

    @classmethod
    def evaluations_total(cls):
        return (cls.iter + 1) * cls.np

    @classmethod
    def func(cls, *args):
        return 0

    @classmethod
    def eval_callback(cls, callback):
        if cls.time is None:
            cls.time = timer()

        cls.evaluations += 1

        new_time = timer()
        callback(cls.evaluations, cls.evaluations_total(), (new_time - cls.time) / cls.evaluations)


class OptIssue1(OptIssueBase):
    desc = 'Issue 1\n' \
           'func: -((psnr - def_psnr) / def_psnr + (bpp - def_bpp) / def_bpp)\n' \
           'params: threshold'
    bounds = [(0, 1)]

    np = 13
    cr = 0.7450
    f = 0.9096
    iter = 31

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
    def get_new_params(result):
        return {"homogeneity_threshold": result.x[0]}


class OptIssue2(OptIssueBase):
    desc = 'Issue 2\nfunc: BCR\nparams: threshold for 3 brightness levels'
    bounds = ((0, 1), (0, 1), (0, 1))

    np = 17
    cr = 0.7122
    f = 0.6301
    iter = 60

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
    def get_new_params(result):
        return {"homogeneity_threshold": result.x}


class OptIssue3(OptIssueBase):
    desc = 'Issue 3\nfunc: PSNR\nparams: offset'
    bounds = ((0, 511), (0, 511))

    np = 10
    cr = 0.4862
    f = 1.1922
    iter = 40

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
    def get_new_params(result):
        return {'offset': array(result.x).astype(int)}


class OptIssue4(OptIssueBase):
    desc = 'Issue 4\nfunc: BCR\nParams: offset'
    bounds = ((0, 511), (0, 511))

    np = 10
    cr = 0.4862
    f = 1.1922
    iter = 40

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
    def get_new_params(result):
        return {'offset': array(result.x).astype(int)}


class OptIssue5(OptIssueBase):
    desc = 'Issue 5\nfunc: PSNR\nparams: max bock size, quantization power, channel scale'
    bounds = ((3, 10), (0.01, 1), (1, 255))

    np = 17
    cr = 0.7122
    f = 0.6301
    iter = 60

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
    def get_new_params(result):
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
    iter = 60

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
    def get_new_params(result):
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
    iter = 166

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
    def get_new_params(result):
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
    iter = 166

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
    def get_new_params(result):
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
    iter = 166

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
    def get_new_params(result):
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
    iter = 166

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
    def get_new_params(result):
        return {
            'homogeneity_threshold': (result.x[0], result.x[1], result.x[2])
        }


ISSUES = [OptIssue1, OptIssue2, OptIssue3, OptIssue4, OptIssue5, OptIssue6, OptIssue7, OptIssue8, OptIssue9,
          OptIssue10]
