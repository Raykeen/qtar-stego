from PIL import Image

from qtar.cli.qtarargparser import get_qtar_argpaser
from qtar.core.qtar import QtarStego
from qtar.experiments.filters import filters
from qtar.optimization.metrics import psnr, bcr


def main():
    argparser = get_qtar_argpaser()
    args = argparser.parse_args()
    params = vars(args)
    test_robustness(params)


def test_robustness(params):
    img = Image.open(params['container'])
    watermark = Image.open(params['watermark'])

    print("{0} in {1}".format(params['watermark'], params['container']))
    print("Threshold: {0}\n"
          "Min - Max block: {1}x{1} - {2}x{2}\n"
          "Quantization power: {3:.2f}\n"
          "Scale: {4:.2f}\n"
          "Offset: {5}\n"
          .format(params['homogeneity_threshold'],
                  params['min_block_size'],
                  params['max_block_size'],
                  params['quant_power'],
                  params['ch_scale'],
                  params['offset']))

    qtar = QtarStego.from_dict(params)
    key_data = qtar.embed(img, watermark)

    stego_image = qtar.get_stego_image()
    wm = qtar.get_wm()

    for filter_name, filter in filters:
        print("FILTER: " + filter_name)
        filtered_stego_image = filter(stego_image)
        extracted_wm = qtar.extract(filtered_stego_image, key_data)

        WM_PSNR = psnr(wm, extracted_wm)
        WM_BCR = bcr(wm, extracted_wm)

        print("PSNR: {0:.4f}dB, WM BCR: {1:.4f}, wmsize: {2}x{3}"
              .format(WM_PSNR, WM_BCR, wm.size[0], wm.size[1]))
        print("## {0} {1}\n".format(WM_PSNR, WM_BCR))
        wm_name = params['watermark'].split("\\")[-1].split(".")[0]
        extracted_wm.save('images\\robustness\\{0} {1}.bmp'.format(wm_name, filter_name))

    print("_"*40+'\n')

if __name__ == "__main__":
    main()
