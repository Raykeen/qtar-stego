from qtar.cli.qtarargparser import get_qtar_argpaser, validate_params
from qtar.experiments import PARAMS_NAMES
from qtar.experiments.compare import qtar_vs_cf_qtar
from qtar.experiments.efficiency import efficiency
from qtar.experiments.enumerations import enumerations
from qtar.experiments.robustness import robustness


def main():
    argparser = get_qtar_argpaser(False)
    argparser.add_argument('experiment', type=str,
                           help='one of the experiments: efficiency, qtar-vs-cfqtar, robustness, enumerations')
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')
    argparser.add_argument('-sheet', '--xls_sheet', metavar='name',
                           type=str, default='enum',
                           help='sheet name of xlsx file')
    argparser.add_argument('-exp', '--experiments_path', metavar='path',
                           type=str, default='experiments/experiments.txt',
                           help='path to list with experiments')
    argparser.add_argument('-P', '--param', metavar='name',
                           type=str, default='quant_power',
                           help='one of: ' + ", ".join(PARAMS_NAMES.keys()))

    args = argparser.parse_args()
    params = validate_params(vars(args))

    xls_path = 'xls/'

    table = []
    if params['experiment'] == 'qtar-vs-cfqtar':
        xls_path += 'qtar_vs_cfqtar'

        table = qtar_vs_cf_qtar(params)

    elif params['experiment'] == 'efficiency':
        xls_path += ('pm_' if params['pm_mode'] else '') \
                    + ('cf_' if params['cf_mode'] else '') \
                    + ('wmdct_' if params['wmdct_mode'] else '') \
                    + 'efficiency'
        table = efficiency(params)

    elif params['experiment'] == 'robustness':
        xls_path += ('pm_' if params['pm_mode'] else '') \
                    + ('cf_' if params['cf_mode'] else '') \
                    + ('wmdct_' if params['wmdct_mode'] else '') \
                    + 'robustness'
        table = robustness(params)
    elif params['experiment'] == 'enumerations':
        xls_path += ('pm_' if params['pm_mode'] else '') \
                    + ('cf_' if params['cf_mode'] else '') \
                    + ('wmdct_' if params['wmdct_mode'] else '') \
                    + params['param'] \
                    + '_enum'
        table = enumerations(params)
    else:
        print('Choose one of the experiments.')
        return

    xls_path += '.xlsx'

    print(table)

    while True:
        try:
            table.to_excel(xls_path, sheet_name=params['xls_sheet'])
            break
        except PermissionError:
            print('Cant save results. Please close %s' % params['xls_path'])
            input()
            continue
