import argparse

from qtar.cli.qtarargparser import get_qtar_argpaser, validate_params
from qtar.cli.embed import embed, get_embed_argparser


def main():
    argparser = argparse.ArgumentParser(prog='qtar', add_help=True,
                                        description='Steganography utility for embedding/extracting secret images '
                                                    'into another images using QTAR algorithm and its modifications.',
                                        formatter_class=argparse.RawTextHelpFormatter)

    subparsers = argparser.add_subparsers(help='Available commands')

    embed_parser = subparsers.add_parser('embed', help='Embed secret image into another image',
                                         parents=[get_embed_argparser()])
    embed_parser.set_defaults(command='embed')

    args = argparser.parse_args()

    if not hasattr(args, 'command'):
        argparser.print_help()
        return

    if args.command == 'embed':
        params = validate_params(vars(args))
        embed(params)


if __name__ == "__main__":
    main()
