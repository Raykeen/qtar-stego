import sys
from copy import copy

from PIL import Image
from scipy.optimize import differential_evolution

from qtar.core.argparser import create_argpaser
from qtar.optimization.deissues import ISSUES
from qtar.cli import embed
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

    argparser = create_argpaser()
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
    params = vars(args)

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
    def_metrics = embed(params)

    de_info = DE_INFO_TEMPLATE.format(i=Issue)
    print(de_info)

    with benchmark("optimized in"):
        de_result = differential_evolution(Issue.func, Issue.bounds,
                                           (container, watermark, params, def_metrics, callback),
                                           strategy='rand1bin',
                                           popsize=Issue.np,
                                           mutation=Issue.f,
                                           recombination=Issue.cr,
                                           polish=False,
                                           maxiter=Issue.iter)
    print(de_result.nit)
    new_params = Issue.get_new_params(de_result)

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
    new_metrics = embed(params)

    if params['xls_path']:
        save_de_results(DE_RESULT_XLS, def_params, new_params, def_metrics, new_metrics)

    return new_metrics


def callback(evaluations, total, time):
    print_progress_bar(evaluations, total, time=time, length=30, file=sys.stderr)


if __name__ == "__main__":
    main()
