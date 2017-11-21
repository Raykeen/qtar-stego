import argparse

from qtar.cli.qtarargparser import validate_params
from qtar.cli.embed import embed, get_embed_argparser
from qtar.cli.extract import extract, get_extract_argparser
from qtar.cli.test import test, get_test_params


def main():
    argparser = argparse.ArgumentParser(prog='qtar', add_help=True,
                                        description='Steganography utility for embedding/extracting secret images '
                                                    'into another images using QTAR algorithm and its modifications.',
                                        formatter_class=argparse.RawTextHelpFormatter)

    subparsers = argparser.add_subparsers(help='Available commands')

    embed_parser = subparsers.add_parser('embed', help='embed secret image into another image',
                                         parents=[get_embed_argparser()])
    embed_parser.set_defaults(command='embed')

    extract_parser = subparsers.add_parser('extract', help='extract image from stego-image',
                                           parents=[get_extract_argparser()])
    extract_parser.set_defaults(command='extract')

    test_parser = subparsers.add_parser('test', help='embed, extract and show detailed info',
                                        parents=[get_test_params()])
    test_parser.set_defaults(command='test')

    args = argparser.parse_args()

    if not hasattr(args, 'command'):
        argparser.print_help()
        return

    if args.command == 'embed':
        params = validate_params(vars(args))
        embed(params)

    elif args.command == 'extract':
        extract(vars(args))

    elif args.command == 'test':
        params = validate_params(vars(args))
        test(params)


if __name__ == "__main__":
    main()
