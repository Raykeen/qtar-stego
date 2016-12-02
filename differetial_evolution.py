import argparse
from scipy.optimize import differential_evolution
from QtarStego import QtarStego, DEFAULT_PARAMS
from test_qtar import test_qtar
from metrics import bcr, psnr
from PIL import Image


class OptIssue1:
    bounds = ((0,1), (0,1), (0,1))

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



def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('container', type=str,
                           help='container image')
    argparser.add_argument('watermark', type=str,
                           help='image to embed into container')
    argparser.add_argument('issue', type=int, default=1,
                           help='1: PSNR optimisation by threshold param for 3 brightness levels')
    argparser.add_argument('--np', type=int, default=20,
                           help='Population size')
    argparser.add_argument('--cr', type=int, default=0.7455,
                           help='Crossover probability')
    argparser.add_argument('--f', type=int, default=0.7455,
                           help='Mutation factor')
    args = argparser.parse_args()

    container = Image.open(args.container).resize((512, 512))
    watermark = Image.open(args.watermark)

    Issue = OptIssue1

    print("DE OPTIMISATION:")
    print('NP: {0}, CR: {1}, F: {2}'.format(args.np, args.cr, args.f))

    de_result = differential_evolution(Issue.func, Issue.bounds, (container, watermark),
                                       strategy='rand1bin',
                                       popsize=args.np, mutation=args.f, recombination=args.cr)

    print("RESULT:")
    params = Issue.get_new_params(de_result)
    params['container'] = args.container
    params['container_size'] = (512, 512)
    params['watermark'] = args.watermark
    params['watermark_size'] = None
    test_qtar(params)

if __name__ == "__main__":
    main()
