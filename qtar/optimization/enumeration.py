import argparse

from PIL import Image
from qtar.optimization.metrics import psnr, bcr

from qtar.core.qtar import QtarStego, DEFAULT_PARAMS


def enumerate_coordinates(img, watermark):
    params = DEFAULT_PARAMS
    params['quant_power'] = 10
    for y in range(0, 255):
        for x in range(0, 255):
            MAXBPP = len(img.getbands()) * 8
            _PSNR = 1
            _BCR = 0
            _Cap = 0
            try:
                params['offset'] = (x, y)
                qtar = QtarStego.from_dict(params)

                key_data = qtar.embed(img, watermark)
                container_image = qtar.get_container_image()
                stego_image = qtar.get_stego_image()
                wm = qtar.get_wm()
                extracted_wm = qtar.extract(stego_image, key_data)
                _PSNR = psnr(container_image, stego_image)
                _BCR = bcr(wm, extracted_wm)
                _Cap = qtar.get_fact_bpp()
                print('{0} {1} {2:.4f} {3:.4f} {4:.4f}'.format(x, y, _PSNR, _BCR, _Cap))
            except:
                print('{0} {1} {2:.4f} {3:.4f} {4:.4f}'.format(x, y, 0, 0, 0))


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('container', type=str,
                           help='container image')
    argparser.add_argument('watermark', type=str,
                           help='image to embed into container')
    args = argparser.parse_args()
    img = Image.open(args.container).resize((256, 256), Image.BILINEAR)
    watermark = Image.open(args.watermark).resize((256, 256), Image.BILINEAR)
    enumerate_coordinates(img, watermark)




if __name__ == "__main__":
    main()
