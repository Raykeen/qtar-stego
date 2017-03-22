import sys
from time import time

from PIL import Image
from qtar.optimization.metrics import psnr, bcr

from qtar.core.qtar import QtarStego, DEFAULT_PARAMS
from qtar.core.argparser import argparser


def main(argv):
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')

    argparser.add_argument('-ns', '--not-save', action='store_true')
    args = argparser.parse_args()
    params = vars(args)
    test_qtar(params)


def test_qtar(params):
    img = Image.open(params['container'])
    if params['container_size']:
        img = img.resize((params['container_size'][0], params['container_size'][1]), Image.BILINEAR)
    watermark = Image.open(params['watermark'])
    if params['watermark_size']:
        watermark = watermark.resize((params['watermark_size'][0], params['watermark_size'][1]), Image.BILINEAR)

    print("{0} in {1}".format(params['watermark'], params['container']))
    print("Threshold: {0}\nMin - Max block: {1}x{1} - {2}x{2}\nQuantization power: {3:.2f}\nScale: {4:.2f}\nOffset: {5}\n"
          .format(params['homogeneity_threshold'],
                  params['min_block_size'],
                  params['max_block_size'],
                  params['quant_power'],
                  params['ch_scale'],
                  params['offset']))

    qtar = QtarStego.from_dict(params)

    embed_time = time()
    key_data = qtar.embed(img, watermark)
    print("embedded in {0:.4f} seconds".format(time() - embed_time))

    container_image = qtar.get_container_image()
    stego_image = qtar.get_stego_image()
    wm = qtar.get_wm()

    if not params['not_save']:
        container_image.save('images\stages\\1-container.bmp')
        qtar.get_qt_image().save('images\stages\\2-quad_tree.bmp')
        qtar.get_dct_image().save('images\stages\\3-dct.bmp')
        qtar.get_ar_image().save('images\stages\\4-adaptive_regions.bmp')
        stego_image.save('images\stages\\6-stego_image.bmp')
        wm.save('images\stages\\5-watermark.bmp')

    extract_time = time()
    extracted_wm = qtar.extract(stego_image, key_data)
    print("extracted in {0:.4f} seconds\n".format(time() - extract_time))

    if not params['not_save']:
        extracted_wm.save('images\stages\\7-extracted_watermark.bmp')

    _BPP = qtar.get_fact_bpp()
    _PSNR = psnr(container_image, stego_image)
    _BCR = bcr(wm, extracted_wm)
    print("{0:.2f}bpp/{1:.4f}bpp, PSNR: {2:.4f}dB, BCR: {3:.4f}, wmsize: {4}x{5}"
          .format(_BPP, qtar.get_available_bpp(),
                  _PSNR, _BCR, wm.size[0], wm.size[1]))
    print("## {0} {1} {2}".format(_PSNR, _BPP, _BCR))
    print("_"*40+'\n')
    return {
        "psnr": _PSNR,
        "bcr": _BCR,
        "bpp": _BPP
    }

if __name__ == "__main__":
    main(sys.argv)
