import argparse

from qtar.cli.qtarargparser import validate_params
from qtar.cli.embed import embed, get_embed_argparser
from qtar.cli.extract import extract, get_extract_argparser
from qtar.cli.test import test, get_test_params


def main():
    argparser = argparse.ArgumentParser(prog='qtar',
                                        add_help=True,
                                        description='Steganography utility for embedding/extracting secret images'
                                                    'into another images using QTAR algorithm and its modifications.')

    subparsers = argparser.add_subparsers(help='Available commands')

    embed_parser = subparsers.add_parser('embed',
                                         help='embed secret image into another image',
                                         description='This command embeds the secret image into\n'
                                                     'the container-image.',
                                         parents=[get_embed_argparser()])
    embed_parser.set_defaults(command='embed')

    extract_parser = subparsers.add_parser('extract',
                                           help='extract image from stego-image',
                                           description='This command extracts the secret image from\n'
                                                       'the stego-image using given key.',
                                           parents=[get_extract_argparser()])
    extract_parser.set_defaults(command='extract')

    test_parser = subparsers.add_parser('test',
                                        help='embed, extract and show detailed info',
                                        description='This command embeds and extracts the secret image\n'
                                                    'into/from given container-image and shows detailed info.',
                                        parents=[get_test_params()],
                                        formatter_class=argparse.RawTextHelpFormatter)
    test_parser.set_defaults(command='test')

    args = argparser.parse_args()

    if not hasattr(args, 'command'):
        argparser.print_help()
        return

    try:
        if args.command == 'embed':
            params = validate_params(vars(args))
            embed(params)

        elif args.command == 'extract':
            extract(vars(args))

        elif args.command == 'test':
            params = validate_params(vars(args))
            test(params)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
