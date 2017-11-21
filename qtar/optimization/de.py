import sys
from copy import copy

from PIL import Image
from scipy.optimize import differential_evolution

from qtar.cli.test import test
from qtar.cli.qtarargparser import get_qtar_argpaser, validate_params
from qtar.optimization.deissues import ISSUES
from qtar.utils import benchmark, print_progress_bar
from qtar.utils.xlsx import save_de_results

DE_RESULT_XLS = "xls\\de.xlsx"

DE_INFO_TEMPLATE = """Differential evolution optimization:
DE params:
NP:   {i.np},
CR:   {i.cr},
F:    {i.f},
Iter: {i.iter}

Optimization issue:
{i.desc}
"""


def main():
    issue_descriptions = ['%d: %s' % (i+1, Issue.desc) for i, Issue in enumerate(ISSUES)]

    argparser = get_qtar_argpaser()
    argparser.add_argument('issue', type=int, default=0,
                           help='0: Run all optimizations\n' + '\n'.join(issue_descriptions))
    argparser.add_argument('-xls', '--xls_path', metavar='path',
                           type=str, default=None,
                           help='save results to xls file')
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')
    args = argparser.parse_args()

    params = validate_params(vars(args))

    if args.issue == 0:
        for Issue in ISSUES:
            run_de(params, Issue)
    else:
        run_de(params, ISSUES[args.issue-1])


def run_de(params, Issue):
    container = Image.open(params['container'])
    if params['container_size']:
        container = container.resize((params['container_size'][0], params['container_size'][1]), Image.BILINEAR)
    watermark = Image.open(params['watermark'])
    if params['watermark_size']:
        watermark = watermark.resize((params['watermark_size'][0], params['watermark_size'][1]), Image.BILINEAR)
    params['save_stages'] = False
    params['key'] = None
    print('Embedding with default params:')
    def_metrics = test(params)

    de_info = DE_INFO_TEMPLATE.format(i=Issue)
    print(de_info)

    with benchmark("optimized in"):
        de_result = differential_evolution(Issue.func, Issue.bounds,
                                           (container, watermark, params, def_metrics, callback),
                                           strategy='rand1bin',
                                           popsize=Issue.np,
                                           mutation=Issue.f,
                                           recombination=Issue.cr,
                                           tol=-1,
                                           atol=-1,
                                           polish=False,
                                           maxiter=Issue.iter)
    print("Iterations done: %s; DE message: %s" % (de_result.nit, de_result.message))
    new_params = Issue.get_new_params(de_result,  params)

    print("\nResult:")
    for name, value in new_params.items():
        if type(value) is float:
            value = "{:.4f}".format(value)
        print("{name}: {value}".format(name=name, value=value))
    print("func: {:.4f}\n".format(de_result.fun))

    print("_" * 40 + '\n')
    print('Embedding with new params:')
    def_params = copy(params)
    params.update(new_params)
    new_metrics = test(params)

    if params['xls_path']:
        while True:
            try:
                save_de_results(DE_RESULT_XLS, def_params, new_params, def_metrics, new_metrics)
                break
            except PermissionError:
                print('Cant save results. Please close %s' % DE_RESULT_XLS, file=sys.stderr)
                input()
                continue

    return new_metrics


def callback(evaluations, total, time, error=None, new_params=None, f=None):
    if f is None:
        f = ''
    print_progress_bar(evaluations, total, time=time, file=sys.stderr, suffix='{:.4f}'.format(f))

    if error:
        print('\n\n' + str(error) + '\n\n' + str(new_params) + '\n', file=sys.stderr)


if __name__ == "__main__":
    main()
