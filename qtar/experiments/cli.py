from qtar.core.argparser import create_argpaser, validate_params
from qtar.experiments.compare import qtar_vs_cf_qtar
from qtar.experiments.efficiency import efficiency


def main():
    argparser = create_argpaser(False)
    argparser.add_argument('experiment', type=str,
                           help='one of the experiments: efficiency, qtar-vs-cfqtar')
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')
    argparser.add_argument('-xls', '--xls_path', metavar='path',
                           type=str, default='xls/experiments.xlsx',
                           help='save results to xls file')
    argparser.add_argument('-sheet', '--xls_sheet', metavar='name',
                           type=str, default=None,
                           help='sheet name of xlsx file')
    argparser.add_argument('-exp', '--experiments_path', metavar='path',
                           type=str, default='experiments/experiments.txt',
                           help='path to list with experiments')

    args = argparser.parse_args()
    params = validate_params(vars(args))

    table = []
    if params['experiment'] == 'qtar-vs-cfqtar':
        if params['xls_sheet'] is None:
            params['xls_sheet'] = 'qtar-vs-cfqtar'

        table = qtar_vs_cf_qtar(params)

    elif params['experiment'] == 'efficiency':
        if params['xls_sheet'] is None:
            params['xls_sheet'] = ('pm' if params['pm_mode'] else '') \
                                  + ('cf' if params['cf_mode'] else '') \
                                  + ('wmdct' if params['wmdct_mode'] else '') \
                                  + 'efficiency'
        table = efficiency(params)

    print(table)

    while True:
        try:
            table.to_excel(params['xls_path'], sheet_name=params['xls_sheet'])
            break
        except PermissionError:
            print('Cant save results. Please close %s' % params['xls_path'])
            input()
            continue
