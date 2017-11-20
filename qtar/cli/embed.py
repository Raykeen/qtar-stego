from PIL import Image

from qtar.core.qtar import QtarStego, NoSpaceError
from qtar.optimization.metrics import psnr, ssim
from qtar.utils import benchmark, extract_filename
from qtar.cli.qtarargparser import get_qtar_argpaser

METRICS_INFO_TEMPLATE = """
PSNR container: {psnr_container:.4f}
SSIM container: {ssim_container:.4f}
BPP:            {bpp:.4f}
key size:       {key.size} """


def get_embed_argparser():
    argparser = get_qtar_argpaser()
    argparser.add_argument('-r', '--container_size', metavar='container size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-R', '--secretimage_size', metavar='secret-image size',
                           type=int, nargs=2, default=None,
                           help='resize secret image')
    argparser.add_argument('-S', '--stego', metavar='stego path',
                           type=int, default=None,
                           help='path to save stego image')
    argparser.add_argument('-key', '--key', metavar='key path',
                           type=str, default='key.qtarkey',
                           help='path to save key')
    return argparser


def embed(params):
    container = Image.open(params['container'])
    if params['container_size']:
        container = container.resize(params['container_size'], Image.BILINEAR)
    watermark = Image.open(params['secret-image'])
    if params['secretimage_size']:
        watermark = watermark.resize(params['secretimage_size'], Image.BILINEAR)

    qtar = QtarStego.from_dict(params)

    try:
        with benchmark("Embedded in "):
            embed_result = qtar.embed(container, watermark, stages=True)
    except NoSpaceError as e:
        print(e)
        return

    stego = embed_result.img_stego
    key = embed_result.key

    if params['stego'] is None:
        stego_path = 'stego_%s.bmp' % extract_filename(params['container'])
    else:
        stego_path = params['stego']

    stego.save(stego_path)
    key.save(params['key'])

    bpp_ = embed_result.bpp
    psnr_container = psnr(container, stego)
    ssim_container = ssim(container, stego)

    metrics_info = METRICS_INFO_TEMPLATE.format(
        psnr_container=psnr_container,
        ssim_container=ssim_container,
        bpp=bpp_,
        key=key
    )

    print(metrics_info)
