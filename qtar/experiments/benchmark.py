from PIL import Image

from qtar.core.qtar import QtarStego
from qtar.optimization.metrics import psnr, bcr, ssim


def embed(params):
    container = Image.open(params['container'])
    if 'container_size' in params and params['container_size']:
        container = container.resize(params['container_size'], Image.BILINEAR)
    watermark = Image.open(params['watermark'])
    if 'watermark_size' in params and params['watermark_size']:
        watermark = watermark.resize(params['watermark_size'], Image.BILINEAR)

    qtar = QtarStego.from_dict(params)

    embed_result = qtar.embed(container, watermark)

    container = embed_result.img_container
    stego = embed_result.img_stego
    wm = embed_result.img_watermark
    key = embed_result.key

    bpp_ = embed_result.bpp
    psnr_container = psnr(container, stego)
    ssim_container = ssim(container, stego)

    extracted_wm = qtar.extract(stego, key)

    bcr_wm = bcr(wm, extracted_wm)
    psnr_wm = psnr(wm, extracted_wm)
    ssim_wm = ssim(wm, extracted_wm)

    return {
        "container psnr": psnr_container,
        "container ssim": ssim_container,
        "watermark psnr": psnr_wm,
        "watermark ssim": ssim_wm,
        "watermark bcr":  bcr_wm,
        "container bpp":  bpp_,
        "key size":       key.size
    }

