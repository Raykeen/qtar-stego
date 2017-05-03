from PIL import Image

from qtar.optimization.metrics import psnr, bcr
from qtar.core.qtar import QtarStego, DEFAULT_PARAMS
from qtar.core.argparser import argparser


def main():
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')
    args = argparser.parse_args()
    params = vars(args)
    enumerate_offset(params)


def enumerate_offset(params):
    container = Image.open(params['container'])
    if params['container_size']:
        container = container.resize((params['container_size'][0], params['container_size'][1]), Image.BILINEAR)
    watermark = Image.open(params['watermark'])
    if params['watermark_size']:
        watermark = watermark.resize((params['watermark_size'][0], params['watermark_size'][1]), Image.BILINEAR)

    print("{0}_in_{1}".format(params['watermark'].split('\\')[-1].replace('.png', ''),
                              params['container'].split('\\')[-1].replace('.png', '')))

    w, h = container.size

    for y in range(0, h):
        for x in range(0, w):
            MAXBPP = len(container.getbands()) * 8
            psnr_ = 1
            bcr_ = 0
            bpp_ = 0
            params['offset'] = (x, y)
            qtar = QtarStego.from_dict(params)

            try:
                embed_result = qtar.embed(container, watermark)
            except:
                print('{0} {1} {2} {3} {4}'.format(x, y, 0, 0, 0))

            container = embed_result.img_container
            stego = embed_result.img_stego
            wm = embed_result.img_watermark
            key = embed_result.key
            ext_wm = qtar.extract(stego, key)
            psnr_ = psnr(container, stego)
            bcr_ = bcr(wm, ext_wm)
            bpp_ = embed_result.bpp
            print('{0} {1} {2} {3} {4}'.format(x, y, psnr_, bcr_, bpp_))


if __name__ == "__main__":
    main()
