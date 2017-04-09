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
    embed_result = qtar.embed(img, watermark, stages=True)
    print("embedded in {0:.4f} seconds".format(time() - embed_time))

    container_image = embed_result.stages_imgs["1-container"]
    stego_image = embed_result.stages_imgs["6-stego_image"]
    wm = embed_result.stages_imgs["5-watermark"]

    if not params['not_save']:
        for name, img in embed_result.stages_imgs.items():
            img.save('images\stages\\' + name + '.bmp')

    extract_time = time()
    extract_stages_imgs = qtar.extract(stego_image, embed_result.key, stages=True)
    print("extracted in {0:.4f} seconds\n".format(time() - extract_time))
    extracted_wm = extract_stages_imgs['9-extracted_watermark']

    if not params['not_save']:
        for name, img in extract_stages_imgs.items():
            img.save('images\stages\\' + name + '.bmp')

    _BPP = embed_result.bpp
    _PSNR = psnr(container_image, stego_image)
    _BCR = bcr(wm, extracted_wm)
    print("{0:.2f}bpp, PSNR: {1:.4f}dB, BCR: {2:.4f}, wmsize: {3}x{4}"
          .format(_BPP, _PSNR, _BCR, wm.size[0], wm.size[1]))
    print("## {0} {1} {2}".format(_PSNR, _BPP, _BCR))
    print("_"*40+'\n')
    return {
        "psnr": _PSNR,
        "bcr": _BCR,
        "bpp": _BPP
    }

if __name__ == "__main__":
    main(sys.argv)
