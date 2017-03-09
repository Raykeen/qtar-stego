import argparse
from time import time

from PIL import Image
from qtar.core.qtar import DEFAULT_PARAMS
from scipy.optimize import differential_evolution

from qtar.optimization.deissues import ISSUES
from qtar.testqtar import test_qtar


def main():
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('container', type=str,
                           help='container image')
    argparser.add_argument('watermark', type=str,
                           help='image to embed into container')
    issue_descriptions = ['%d: %s' % (i+1, Issue.desc) for i, Issue in enumerate(ISSUES)]
    argparser.add_argument('issue', type=int, default=0,
                           help='0: Run all optimizations\n' + '\n'.join(issue_descriptions))
    args = argparser.parse_args()

    if args.issue == 0:
        for Issue in ISSUES:
            run_de(args.container, args.watermark, Issue)
    else:
        run_de(args.container, args.watermark, ISSUES[args.issue-1])


def run_de(container_path, watermark_path, Issue):
    container = Image.open(container_path).resize((512, 512))
    watermark = Image.open(watermark_path)
    def_params = DEFAULT_PARAMS
    def_params["container"] = container_path
    def_params["watermark"] = watermark_path
    def_params['container_size'] = (512, 512)
    def_params['watermark_size'] = None
    def_params['not_save'] = True
    def_results = test_qtar(def_params)

    print("DE OPTIMISATION:")
    print(Issue.desc)
    print("\nDE PARAMS:")
    print('NP: {0}, CR: {1}, F: {2}, Iter: {3}'.format(Issue.np, Issue.cr, Issue.f, Issue.iter))

    de_time = time()

    de_result = differential_evolution(Issue.func, Issue.bounds, (container, watermark, def_results),
                                       strategy='rand1bin',
                                       popsize=Issue.np,
                                       mutation=Issue.f,
                                       recombination=Issue.cr,
                                       tol=0,
                                       maxiter=Issue.iter)
    print("\noptimized in {0} seconds".format(time() - de_time))

    print("\nRESULT:")
    params = Issue.get_new_params(de_result)
    params['container'] = container_path
    params['container_size'] = (512, 512)
    params['watermark'] = watermark_path
    params['watermark_size'] = None
    params['not_save'] = True
    print("\nTEST:")
    test_qtar(params)

if __name__ == "__main__":
    main()
