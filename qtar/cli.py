import os

from PIL import Image

from qtar.core.qtar import QtarStego
from qtar.core.argparser import argparser
from qtar.optimization.metrics import psnr, bcr
from qtar.utils import benchmark

STAGES_DIR = "stages\\"
EMBEDDING_INFO_TEMPLATE = """Embedding {watermark} in {container} using QTAR

QTAR params:
threshold:             {homogeneity_threshold}
min - max block sizes: {min_block_size} - {max_block_size}
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


def main():
    argparser.add_argument('-rc', '--container_size', metavar='container_size',
                           type=int, nargs=2, default=None,
                           help='resize container image')
    argparser.add_argument('-rw', '--watermark_size', metavar='watermark_size',
                           type=int, nargs=2, default=None,
                           help='resize watermark')
    argparser.add_argument('-ss', '--save-stages', action='store_true',
                           help='save stages images in "stages" directory')
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

    if params['save-stages']:
        save_stages(embed_result.stages_imgs)

    with benchmark("extracted in"):
        extract_stages_imgs = qtar.extract(stego, embed_result.key, stages=True)
    extracted_wm = extract_stages_imgs['9-extracted_watermark']

    if params['save-stages']:
        save_stages(extract_stages_imgs)

    bpp_ = embed_result.bpp
    psnr_ = psnr(container, stego)
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


def save_stages(stages):
    for name, img in stages.items():
        if not os.path.exists(STAGES_DIR):
            os.makedirs(STAGES_DIR)
        img.save(STAGES_DIR + name + '.bmp')


if __name__ == "__main__":
    main()
