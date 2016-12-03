import sys
import argparse
from metrics import psnr, bcr
from QtarStego import QtarStego, DEFAULT_PARAMS
from PIL import Image


def main(argv):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('container', type=str,
                           help='container image')
    argparser.add_argument('watermark', type=str,
                           help='image to embed into container')
    argparser.add_argument('-ns', '--not-save', action='store_true')
    argparser.add_argument('-t', '--homogeneity_threshold', metavar='threshold',
                           type=float, nargs='+', default=DEFAULT_PARAMS['homogeneity_threshold'],
                           help='homogeneity thresholds for different brightness levels   float[0, 1])')
    argparser.add_argument('-min', '--min_block_size', metavar='size',
                           type=int, default=DEFAULT_PARAMS['min_block_size'],
                           help='min block size   int[2, max_block_size], square of 2')
    argparser.add_argument('-max', '--max_block_size', metavar='size',
                           type=int, default=DEFAULT_PARAMS['max_block_size'],
                           help='max block size   int[min_block_size, image_size], square of 2')
    argparser.add_argument('-q', '--quant_power', metavar='power',
                           type=float, default=DEFAULT_PARAMS['quant_power'],
                           help='quantization power   float(0, 1]')
    argparser.add_argument('-s', '--ch_scale', metavar='scale',
                           type=float, default=DEFAULT_PARAMS['ch_scale'],
                           help='scale to ch_scale watermark pixels values before embedding   float(0, 255]')
    argparser.add_argument('-o', '--offset', metavar='offset',
                           type=int, nargs=2, default=DEFAULT_PARAMS['offset'],
                           help='offset container image')
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')
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
    print("Threshold: {0}\nMin - Max block: {1}x{1} - {2}x{2}\nQuantization power: {3}\nScale: {4}\nOffset: {5}\n"
          .format(params['homogeneity_threshold'],
                  params['min_block_size'],
                  params['max_block_size'],
                  params['quant_power'],
                  params['ch_scale'],
                  params['offset']))

    qtar = QtarStego.from_dict(params)

    key_data = qtar.embed(img, watermark)
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

    extracted_wm = qtar.extract(stego_image, key_data)

    if not params['not_save']:
        extracted_wm.save('images\stages\\7-extracted_watermark.bmp')

    print("{0:.2f}bpp/{1:.2f}bpp, PSNR: {2:.2f}dB, BCR: {3:.2f}, wmsize: {4}x{5}"
          .format(qtar.get_fact_bpp(), qtar.get_available_bpp(),
                  psnr(container_image, stego_image),
                  bcr(wm, extracted_wm), wm.size[0], wm.size[1]))

if __name__ == "__main__":
    main(sys.argv)
