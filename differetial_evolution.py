import argparse
from scipy.optimize import differential_evolution
from numpy import array
from QtarStego import QtarStego, DEFAULT_PARAMS
from test_qtar import test_qtar
from metrics import bcr, psnr
from math import sqrt
from PIL import Image


class OptIssue1:
    desc = 'Issue 1\nFunc: PSNR\nParams: Threshold for 3 brightness levels'
    bounds = ((0, 1), (0, 1), (0, 1))

    np = 17
    cr = 0.7122
    f = 0.6301
    iter = 60

    @staticmethod
    def func(threshold, container, watermark):
        qtar = QtarStego(threshold)

        qtar.embed(container, watermark)
        container_image = qtar.get_container_image()
        stego_image = qtar.get_stego_image()
        return -psnr(container_image, stego_image)

    @staticmethod
    def get_new_params(result):
        print('Threshold: {0:.2f} {1:.2f} {2:.2f},\nPSNR: {3:.2f},\nIter: {4}'
              .format(result.x[0], result.x[1], result.x[2], -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['homogeneity_threshold'] = result.x
        return params


class OptIssue2:
    desc = 'Issue 2\nFunc: BCR\nParams: Threshold for 3 brightness levels'
    bounds = ((0, 1), (0, 1), (0, 1))

    np = 17
    cr = 0.7122
    f = 0.6301
    iter = 60

    @staticmethod
    def func(threshold, container, watermark):
        qtar = QtarStego(threshold)

        key_data = qtar.embed(container, watermark)
        stego_image = qtar.get_stego_image()
        watermark = qtar.get_wm()
        extracted_wm = qtar.extract(stego_image, key_data)
        return -bcr(watermark, extracted_wm)

    @staticmethod
    def get_new_params(result):
        print('Threshold: {0:.2f} {1:.2f} {2:.2f},\nBCR: {3:.2f},\nIter: {4}'
              .format(result.x[0], result.x[1], result.x[2], -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['homogeneity_threshold'] = result.x
        return params


class OptIssue3:
    desc = 'Issue 3\nFunc: PSNR\nParams: Offset'
    bounds = ((0, 511), (0, 511))

    np = 10
    cr = 0.4862
    f = 1.1922
    iter = 40

    @staticmethod
    def func(offset, container, watermark):
        qtar = QtarStego(offset=array(offset).astype(int))

        qtar.embed(container, watermark)
        container_image = qtar.get_container_image()
        stego_image = qtar.get_stego_image()
        return -psnr(container_image, stego_image)

    @staticmethod
    def get_new_params(result):
        print('Offset: {0}, PSNR: {1:.2f}, Iter: {2}'.format(array(result.x).astype(int), -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['offset'] = array(result.x).astype(int)
        return params


class OptIssue4:
    desc = 'Issue 4\nFunc: BCR\nParams: Offset'
    bounds = ((0, 511), (0, 511))

    np = 10
    cr = 0.4862
    f = 1.1922
    iter = 40

    @staticmethod
    def func(offset, container, watermark):
        qtar = QtarStego(offset=array(offset).astype(int))

        key_data = qtar.embed(container, watermark)
        stego_image = qtar.get_stego_image()
        watermark = qtar.get_wm()
        extracted_wm = qtar.extract(stego_image, key_data)
        return -bcr(watermark, extracted_wm)

    @staticmethod
    def get_new_params(result):
        print('Offset: {0}, BCR: {1:.2f}, Iter: {2}'.format(array(result.x).astype(int), -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['offset'] = array(result.x).astype(int)
        return params


class OptIssue5:
    desc = 'Issue 5\nFunc: PSNR\nParams: max bock size, quant power, channel scale'
    bounds = ((3, 10), (0.01, 1), (1,  255))

    np = 17
    cr = 0.7122
    f = 0.6301
    iter = 60

    @staticmethod
    def func(args, container, watermark):
        max_b = 2**int(args[0])
        qp = args[1]
        sc = args[2]
        qtar = QtarStego(max_block_size=max_b, quant_power=qp, ch_scale=sc)

        qtar.embed(container, watermark)
        container_image = qtar.get_container_image()
        stego_image = qtar.get_stego_image()
        return -psnr(container_image, stego_image)

    @staticmethod
    def get_new_params(result):
        print('Max block size: {0}, Quant power: {1:.2f}, Channel scale: {2:.2f}, PSNR: {3:.2f}, Iter: {4}'
              .format(2**int(result.x[0]), result.x[1], result.x[2], -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['max_block_size'] = 2**int(result.x[0])
        params['quant_power'] = result.x[1]
        params['ch_scale'] = result.x[2]
        return params


class OptIssue6:
    desc = 'Issue 6\nFunc: BCR\nParams: max bock size, quant power, channel scale'
    bounds = ((3, 10), (0.01, 1), (1,  255))

    np = 17
    cr = 0.7122
    f = 0.6301
    iter = 60

    @staticmethod
    def func(args, container, watermark):
        max_b = 2**int(args[0])
        qp = args[1]
        sc = args[2]
        qtar = QtarStego(max_block_size=max_b, quant_power=qp, ch_scale=sc)

        key_data = qtar.embed(container, watermark)
        stego_image = qtar.get_stego_image()
        watermark = qtar.get_wm()
        extracted_wm = qtar.extract(stego_image, key_data)
        return -bcr(watermark, extracted_wm)

    @staticmethod
    def get_new_params(result):
        print('Max block size: {0}, Quant power: {1:.2f}, Channel scale: {2:.2f}, BCR: {3:.3f}, Iter: {4}'
              .format(2**int(result.x[0]), result.x[1], result.x[2], -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['max_block_size'] = 2**int(result.x[0])
        params['quant_power'] = result.x[1]
        params['ch_scale'] = result.x[2]
        return params


class OptIssue7:
    desc = 'Issue 7\nFunc: Universal\nParams: th1, th2, th3 ,min bock size, max bock size, quant power, channel scale'
    bounds = ((0, 1), (0, 1), (0, 1), (3, 10), (3, 10), (0.01, 1), (1,  255))

    np = 12
    cr = 0.2368
    f = 0.6702
    iter = 166

    @staticmethod
    def func(args, container, watermark):
        th = (args[0], args[1], args[2])
        max_b = 2**int(args[3])
        min_b = 2**int(args[4])
        if min_b>max_b:
            max_b = min_b
        qp = args[5]
        sc = args[6]
        qtar = QtarStego(homogeneity_threshold=th,
                         min_block_size=min_b,
                         max_block_size=max_b,
                         quant_power=qp,
                         ch_scale=sc)

        MAXBPP = len(container.getbands()) * 8
        _PSNR = 1
        _BCR = 0
        _Cap = 0
        try:
            key_data = qtar.embed(container, watermark)
            container_image = qtar.get_container_image()
            stego_image = qtar.get_stego_image()
            watermark = qtar.get_wm()
            extracted_wm = qtar.extract(stego_image, key_data)
            _PSNR = psnr(container_image, stego_image)
            _BCR = bcr(watermark, extracted_wm)
            _Cap = qtar.get_fact_bpp()
        except:
            return 1

        return sqrt((-1 / _PSNR)**2 + (1 - _BCR)**2 + (1 - _Cap / MAXBPP)**2)

    @staticmethod
    def get_new_params(result):
        max_b = 2 ** int(result.x[3])
        min_b = 2 ** int(result.x[4])
        if min_b > max_b:
            max_b = min_b
        print('Threshold: {0:.2f} {1:.2f} {2:.2f}, \n'
              'Min block size: {3}, \n'
              'Max block size: {4}, \n'
              'Quant power: {5:.2f}, \n'
              'Channel scale: {6:.2f}, \n'
              'Func: {7:.2f}, Iter: {8}'
              .format(result.x[0],
                      result.x[1],
                      result.x[2],
                      min_b,
                      max_b,
                      result.x[5],
                      result.x[6],
                      result.fun,
                      result.nit))

        params = DEFAULT_PARAMS.copy()
        params['homogeneity_threshold'] = (result.x[0], result.x[1], result.x[2])
        params['min_block_size'] = min_b
        params['max_block_size'] = max_b
        params['quant_power'] = result.x[5]
        params['ch_scale'] = result.x[6]
        return params

ISSUES = [OptIssue1, OptIssue2, OptIssue3, OptIssue4, OptIssue5, OptIssue6, OptIssue7]


def main():
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('container', type=str,
                           help='container image')
    argparser.add_argument('watermark', type=str,
                           help='image to embed into container')
    argparser.add_argument('issue', type=int, default=0,
                           help='0: Run all optimizations\n' +
                                '1: {}\n'.format(OptIssue1.desc) +
                                '2: {}\n'.format(OptIssue2.desc) +
                                '3: {}\n'.format(OptIssue3.desc) +
                                '4: {}\n'.format(OptIssue4.desc) +
                                '5: {}\n'.format(OptIssue5.desc) +
                                '6: {}\n'.format(OptIssue6.desc))
    args = argparser.parse_args()

    if args.issue == 0:
        for Issue in ISSUES:
            run_de(args.container, args.watermark, Issue)
    else:
        run_de(args.container, args.watermark, ISSUES[args.issue-1])


def run_de(container_path, watermark_path, Issue):
    container = Image.open(container_path).resize((512, 512))
    watermark = Image.open(watermark_path)
    print("DE OPTIMISATION:")
    print(Issue.desc)
    print("DE PARAMS:")
    print('NP: {0}, CR: {1}, F: {2}, Iter: {3}'.format(Issue.np, Issue.cr, Issue.f, Issue.iter))

    de_result = differential_evolution(Issue.func, Issue.bounds, (container, watermark),
                                       strategy='rand1bin',
                                       popsize=Issue.np,
                                       mutation=Issue.f,
                                       recombination=Issue.cr,
                                       tol=0,
                                       maxiter=Issue.iter)

    print("RESULT:")
    params = Issue.get_new_params(de_result)
    params['container'] = container_path
    params['container_size'] = (512, 512)
    params['watermark'] = watermark_path
    params['watermark_size'] = None
    params['not_save'] = True
    print("TEST:")
    test_qtar(params)

if __name__ == "__main__":
    main()
