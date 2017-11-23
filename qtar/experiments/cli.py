import os

from qtar.cli.qtarargparser import get_qtar_argpaser, validate_params
from qtar.experiments import PARAMS_NAMES
from qtar.experiments.compare import qtar_vs_cf_qtar
from qtar.experiments.efficiency import efficiency
from qtar.experiments.enumerations import enumerations
from qtar.experiments.robustness import robustness


def main():
    argparser = get_qtar_argpaser(False)
    argparser.add_argument('experiment',
                           type=str,
                           choices=['efficiency', 'qtar-vs-cfqtar', 'robustness', 'enumerations'],
                           help='one of the experiments: efficiency, qtar-vs-cfqtar, robustness, enumerations')

    argparser.add_argument('-r', '--rc',
                           dest='container_size',
                           metavar='CONTAINER_SIZE',
                           type=int,
                           nargs=2,
                           default=None,
                           help='Resize container image.')

    argparser.add_argument('-R', '--rsi',
                           dest='watermark_size',
                           metavar='SECRET_IMAGE_SIZE',
                           type=int,
                           nargs=2,
                           default=None,
                           help='Resize secret image.')

    argparser.add_argument('-e', '--experiments',
                           metavar='EXPERIMENTS_PATH',
                           type=str,
                           default='experiments/experiments.txt',
                           help='path to list with experiments')

    argparser.add_argument('-P', '--param',
                           metavar='PARAM_TO_ENUMERATE',
                           type=str,
                           default='quant_power',
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

    os.makedirs(os.path.dirname(xls_path), exist_ok=True)

    while True:
        try:
            table.to_excel(xls_path, sheet_name='enum')
            break
        except PermissionError:
            print('Cant save results. Please close %s' % params['xls_path'])
            input()
            continue


if __name__ == "__main__":
    main()