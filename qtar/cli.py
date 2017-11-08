import os

from PIL import Image

from qtar.core.qtar import QtarStego, NoSpaceError
from qtar.core.argparser import create_argpaser, validate_params
from qtar.core.container import Key
from qtar.optimization.metrics import psnr, bcr, ssim
from qtar.utils import benchmark
from qtar.utils.stamp import stamp_image

STAGES_DIR = "stages\\"
EMBEDDING_INFO_TEMPLATE = """Embedding {watermark} in {container} using QTAR

QTAR params:
pm mode:               {pm_mode}
cf mode:               {cf_mode}
wmdct mode:            {wmdct_mode}
threshold:             {homogeneity_threshold}
min - max block sizes: {min_block_size} - {max_block_size}
watermark block size:  {wmdct_block_size}
quantization power:    {quant_power:.2f}
cf grid size:          {cf_grid_size}
scale:                 {ch_scale:.2f}
offset:                {offset}
"""
METRICS_INFO_TEMPLATE = """
Metrics:
PSNR container: {psnr_container:.4f}
SSIM container: {ssim_container:.4f}
PSNR watermark: {psnr_wm:.4f}
SSIM watermark: {ssim_wm:.4f}
BPP:     {bpp:.4f}
BCR:     {bcr:.4f}
WM_SIZE: {width}x{height}"""
STAMP_TEMPLATE = """pm mode:    {use_permutations}
threshold:  {homogeneity_threshold}
block size: {min_block_size}px - {max_block_size}px
wm block:   {wmdct_block_size}px
q power:    {quant_power:.2f}
cf grid:    {cf_grid_size}px
k:          {ch_scale:.2f}
offset:     {offset[0]}px {offset[1]}px
BPP:        {bpp:.4f}
PSNR:       {psnr:.4f}
SSIM:       {ssim:.4f}"""
KEY_INFO_TEMPLATE = """  
Key size info (bytes):  
key size:    {key.size}  
params size: {key.params_size}  
qt key size: {key.qt_key_size}  
cf key size: {key.cf_key_size}
pm key size: {key.pm_fix_key_size}
"""


def main():
    argparser = create_argpaser()
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')
    argparser.add_argument('-ss', '--save_stages', action='store_true',
                           help='save stages images in "stages" directory')
    argparser.add_argument('-st', '--stamp_stages', action='store_true',
                           help='stamp info on stages images')
    argparser.add_argument('-key', '--key', metavar='path',
                           type=str, default=None,
                           help='save key to file')
    args = argparser.parse_args()
    params = validate_params(vars(args))

    embed(params)


def embed(params):
    container = Image.open(params['container'])
    if params['container_size']:
        container = container.resize(params['container_size'], Image.BILINEAR)
    watermark = Image.open(params['watermark'])
    if params['watermark_size']:
        watermark = watermark.resize(params['watermark_size'], Image.BILINEAR)

    embedding_info = EMBEDDING_INFO_TEMPLATE.format(**params)
    print(embedding_info)

    qtar = QtarStego.from_dict(params)

    try:
        with benchmark("embedded in "):
            embed_result = qtar.embed(container, watermark, stages=True)
    except NoSpaceError as e:
        print(e)
        return

    container = embed_result.img_container
    stego = embed_result.img_stego
    wm = embed_result.img_watermark
    key = embed_result.key

    bpp_ = embed_result.bpp
    psnr_container = psnr(container, stego)
    ssim_container = ssim(container, stego)

    if 'save_stages' in params and params['save_stages']:
        save_stages(embed_result.stages_imgs, STAMP_TEMPLATE.format(
            **params,
            psnr=psnr_container,
            ssim=ssim_container,
            bpp=bpp_
        ) if params['stamp_stages'] else None)

    if 'key' in params and params['key']:
        key.save(params['key'])
        key = Key.open(params['key'])

    key_info = KEY_INFO_TEMPLATE.format(key=key)
    print(key_info)

    with benchmark("extracted in"):
        extract_stages_imgs = qtar.extract(stego, key, stages=True)
    extracted_wm = extract_stages_imgs['9-extracted_watermark']

    if 'save_stages' in params and params['save_stages']:
        save_stages(extract_stages_imgs, STAMP_TEMPLATE.format(
            **params,
            psnr=psnr_container,
            ssim=ssim_container,
            bpp=bpp_
        ) if params['stamp_stages'] else None)

    bcr_wm = bcr(wm, extracted_wm)
    psnr_wm = psnr(wm, extracted_wm)
    ssim_wm = ssim(wm, extracted_wm)

    metrics_info = METRICS_INFO_TEMPLATE.format(
        psnr_container=psnr_container,
        ssim_container=ssim_container,
        psnr_wm=psnr_wm,
        ssim_wm=ssim_wm,
        bpp=bpp_,
        bcr=bcr_wm,
        width=wm.size[0],
        height=wm.size[1]
    )
    print(metrics_info)
    print("_"*40+'\n')
    return {
        "container psnr": psnr_container,
        "container ssim": ssim_container,
        "watermark psnr": psnr_wm,
        "watermark ssim": ssim_wm,
        "watermark bcr": bcr_wm,
        "container bpp": bpp_
    }


def save_stages(stages, stamp_txt=None):
    for name, img in stages.items():
        if not os.path.exists(STAGES_DIR):
            os.makedirs(STAGES_DIR)
        if stamp_txt is not None:
            img = stamp_image(img, stamp_txt)
        img.save(STAGES_DIR + name + '.bmp')


if __name__ == "__main__":
    main()
