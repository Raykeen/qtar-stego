from time import time

from PIL import Image
from qtar.core.qtar import DEFAULT_PARAMS
from scipy.optimize import differential_evolution

from qtar.core.argparser import argparser
from qtar.optimization.deissues import ISSUES
from qtar.cli import embed
from qtar.utils import benchmark


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
    argparser.add_argument('issue', type=int, default=0,
                           help='0: Run all optimizations\n' + '\n'.join(issue_descriptions))
    args = argparser.parse_args()

    if args.issue == 0:
        for Issue in ISSUES:
            run_de(args, Issue)
    else:
        run_de(args, ISSUES[args.issue-1])


if __name__ == "__main__":
    main()


def run_de(params, Issue):
    container = Image.open(params['container'])
    if params['container_size']:
        container = container.resize((params['container_size'][0], params['container_size'][1]), Image.BILINEAR)
    watermark = Image.open(params['watermark'])
    if params['watermark_size']:
        watermark = watermark.resize((params['watermark_size'][0], params['watermark_size'][1]), Image.BILINEAR)
    params['container_size'] = (512, 512)
    params['watermark_size'] = None
    params['not_save'] = True
    default_metrics = embed(params)

    de_info = DE_INFO_TEMPLATE.format(i=Issue)
    print(de_info)

    with benchmark("optimized in"):
        de_result = differential_evolution(Issue.func, Issue.bounds, (container, watermark, default_metrics),
                                           strategy='rand1bin',
                                           popsize=Issue.np,
                                           mutation=Issue.f,
                                           recombination=Issue.cr,
                                           tol=0,
                                           maxiter=Issue.iter)

    print("\nResult:")
    new_params = Issue.get_new_params(de_result)
    params.update(new_params)
    return embed(params)


