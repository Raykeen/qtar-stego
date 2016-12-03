import argparse
from scipy.optimize import differential_evolution
from QtarStego import QtarStego, DEFAULT_PARAMS
from test_qtar import test_qtar
from metrics import bcr, psnr
from PIL import Image


class OptIssue1:
    desc = 'Func: PSNR Params: Threshold for 3 brightness levels'
    bounds = ((0, 1), (0, 1), (0, 1))

    @staticmethod
    def func(threshold, container, watermark):
        qtar = QtarStego(threshold)

        qtar.embed(container, watermark)
        container_image = qtar.get_container_image()
        stego_image = qtar.get_stego_image()
        return -psnr(container_image, stego_image)

    @staticmethod
    def get_new_params(result):
        print('Threshold: {0}, PSNR: {1}, Iter: {2}'.format(result.x, -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['homogeneity_threshold'] = result.x
        return params


class OptIssue2:
    desc = 'Func: BCR Params: Threshold for 3 brightness levels'
    bounds = ((0, 1), (0, 1), (0, 1))

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
        print('Threshold: {0}, BCR: {1}, Iter: {2}'.format(result.x, -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['homogeneity_threshold'] = result.x
        return params


class OptIssue3:
    desc = 'Func: PSNR Params: Offset'
    bounds = ((0, 511), (0, 511))

    @staticmethod
    def func(offset, container, watermark):
        qtar = QtarStego(offset=offset)

        qtar.embed(container, watermark)
        container_image = qtar.get_container_image()
        stego_image = qtar.get_stego_image()
        return -psnr(container_image, stego_image)

    @staticmethod
    def get_new_params(result):
        print('Offset: {0}, PSNR: {1}, Iter: {2}'.format(result.x, -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['offset'] = result.x
        return params


class OptIssue4:
    desc = 'Func: BCR Params: Offset'
    bounds = ((0, 511), (0, 511))

    @staticmethod
    def func(offset, container, watermark):
        qtar = QtarStego(offset=offset)

        key_data = qtar.embed(container, watermark)
        stego_image = qtar.get_stego_image()
        watermark = qtar.get_wm()
        extracted_wm = qtar.extract(stego_image, key_data)
        return -bcr(watermark, extracted_wm)

    @staticmethod
    def get_new_params(result):
        print('Offset: {0}, BCR: {1}, Iter: {2}'.format(result.x, -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['offest'] = result.x
        return params


class OptIssue5:
    desc = 'Func: PSNR Params: max bock size, quant power, channel scale'
    bounds = ((3, 9), (0.01, 1), (1,  255))

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
        print('Max block size: {0}, Quant power: {1}, Channel scale: {2}, PSNR: {3}, Iter: {4}'
              .format(result.x[0], result.x[1], result.x[2], -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['max_block_size'] = result.x[0]
        params['quant_power'] = result.x[1]
        params['ch_scale'] = result.x[2]
        return params


class OptIssue6:
    desc = 'Func: BCR Params: max bock size, quant power, channel scale'
    bounds = ((3, 9), (0.01, 1), (1,  255))

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
        print('Max block size: {0}, Quant power: {1}, Channel scale: {2}, PSNR: {3}, Iter: {4}'
              .format(result.x[0], result.x[1], result.x[2], -result.fun, result.nit))

        params = DEFAULT_PARAMS.copy()
        params['max_block_size'] = result.x[0]
        params['quant_power'] = result.x[1]
        params['ch_scale'] = result.x[2]
        return params

ISSUES = [OptIssue1, OptIssue2, OptIssue3, OptIssue4, OptIssue5, OptIssue6]


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
    argparser.add_argument('--np', type=int, default=20,
                           help='Population size')
    argparser.add_argument('--cr', type=int, default=0.7455,
                           help='Crossover probability')
    argparser.add_argument('--f', type=int, default=0.7455,
                           help='Mutation factor')
    args = argparser.parse_args()

    if args.issue == 0:
        for Issue in ISSUES:
            run_de(args.container, args.watermark, args.np, args.cr, args.f, Issue)
    else:
        run_de(args.container, args.watermark, args.np, args.cr, args.f, ISSUES[args.issue])


def run_de(container_path, watermark_path, np, cr, f, Issue):
    container = Image.open(container_path).resize((512, 512))
    watermark = Image.open(watermark_path)
    print("DE OPTIMISATION:")
    print('NP: {0}, CR: {1}, F: {2}'.format(np, cr, f))

    de_result = differential_evolution(Issue.func, Issue.bounds, (container, watermark),
                                       strategy='rand1bin',
                                       popsize=np, mutation=f, recombination=cr)

    print("RESULT:")
    params = Issue.get_new_params(de_result)
    params['container'] = container_path
    params['container_size'] = (512, 512)
    params['watermark'] = watermark_path
    params['watermark_size'] = None
    params['not_save'] = True
    test_qtar(params)
    print("_"*40+'\n')

if __name__ == "__main__":
    main()
