import argparse
from PIL import Image

from qtar.core.qtar import QtarStego
from qtar.core.container import Key
from qtar.utils import benchmark, extract_filename, save_file


def get_extract_argparser():
    argparser = argparse.ArgumentParser(add_help=False)

    argparser.add_argument('stego', metavar='<stego file>',
                           type=str, help='path to stego image')
    argparser.add_argument('key', metavar='<key file>',
                           type=str, default='key.qtarkey',
                           help='path to key')
    argparser.add_argument('-e', dest='si_path', metavar='<path to save>', default=None,
                           type=str, help='path to save extracted image')

    return argparser


def extract(params):
    key = Key.open(params['key'])
    stego_image = Image.open(params['stego'])

    with benchmark("extracted in"):
        secret_image = QtarStego.extract(stego_image, key)

    if params['si_path']:
        si_path = params['si_path']
    else:
        stego_image_file_name = extract_filename(params['stego'])
        si_path = 'extracted_from_%s.png' % stego_image_file_name

    save_file(secret_image, si_path)
