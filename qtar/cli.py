import os

from PIL import Image

from qtar.core.qtar import QtarStego
from qtar.core.argparser import argparser
from qtar.core.container import Key
from qtar.optimization.metrics import psnr, bcr
from qtar.utils import benchmark
from qtar.utils.stamp import stamp_image

STAGES_DIR = "stages\\"
EMBEDDING_INFO_TEMPLATE = """Embedding {watermark} in {container} using QTAR

QTAR params:
threshold:             {homogeneity_threshold}
min - max block sizes: {min_block_size} - {max_block_size}
watermark block size:  {wm_block_size}
quantization power:    {quant_power:.2f}
scale:                 {ch_scale:.2f}
offset:                {offset}
"""
METRICS_INFO_TEMPLATE = """
Metrics:
PSNR:    {psnr:.4f}
BPP:     {bpp:.4f}
BCR:     {bcr:.4f}
WM_SIZE: {width}x{height}"""
STAMP_TEMPLATE = """threshold:  {homogeneity_threshold}
block size: {min_block_size}px - {max_block_size}px
wm block:   {wm_block_size}px
q power:    {quant_power:.2f}
k:          {ch_scale:.2f}
offset:     {offset[0]}px {offset[1]}px
BPP:        {bpp:.4f}
PSNR:       {psnr:.4f}"""
KEY_INFO_TEMPLATE = """  
Key size info (bytes):  
key size:    {key.size}  
params size: {key.params_size}  
qt key size: {key.qt_key_size}  
ar key size: {key.ar_key_size}
"""


def main():
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
    params = vars(args)
    embed(params)


def embed(params):
    container = Image.open(params['container'])
    if params['container_size']:
        container = container.resize((params['container_size'][0], params['container_size'][1]), Image.BILINEAR)
    watermark = Image.open(params['watermark'])
    if params['watermark_size']:
        watermark = watermark.resize((params['watermark_size'][0], params['watermark_size'][1]), Image.BILINEAR)

    embedding_info = EMBEDDING_INFO_TEMPLATE.format(**params)
    print(embedding_info)

    qtar = QtarStego.from_dict(params)

    with benchmark("embedded in "):
        embed_result = qtar.embed(container, watermark, stages=True)

    container = embed_result.img_container
    stego = embed_result.img_stego
    wm = embed_result.img_watermark
    key = embed_result.key

    bpp_ = embed_result.bpp
    psnr_ = psnr(container, stego)

    if params['save_stages']:
        save_stages(embed_result.stages_imgs, STAMP_TEMPLATE.format(
            **params,
            psnr=psnr_,
            bpp=bpp_
        ) if params['stamp_stages'] else None)

    if params['key']:
        key.save(params['key'])
        key = Key.open(params['key'])

    key_info = KEY_INFO_TEMPLATE.format(key=key)
    print(key_info)

    with benchmark("extracted in"):
        extract_stages_imgs = qtar.extract(stego, key, stages=True)
    extracted_wm = extract_stages_imgs['9-extracted_watermark']

    if params['save_stages']:
        save_stages(extract_stages_imgs, STAMP_TEMPLATE.format(
            **params,
            psnr=psnr_,
            bpp=bpp_
        ) if params['stamp_stages'] else None)

    bcr_ = bcr(wm, extracted_wm)

    metrics_info = METRICS_INFO_TEMPLATE.format(
        psnr=psnr_,
        bpp=bpp_,
        bcr=bcr_,
        width=wm.size[0],
        height=wm.size[1]
    )
    print(metrics_info)
    print("_"*40+'\n')
    return {
        "container psnr": psnr_,
        "watermark bcr": bcr_,
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
