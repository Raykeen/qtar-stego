TEST_IMAGES_PATH = 'images\\'

PARAMS_NAMES = {
    'homogeneity_threshold': 'th',
    'min_block_size': 'min_b, px',
    'max_block_size': 'max_b, px',
    'quant_power': 'q',
    'ch_scale': 'k',
    'offset': ('x, px', 'y, px'),
    'pm_mode': 'pm',
    'cf_mode': 'cf',
    'cf_grid_size': 'cf, px',
    'wmdct_mode': 'wmdct',
    'wmdct_block_size': 'v, px',
    'wmdct_scale': 'sk'
}

METRICS_NAMES = {
    'container psnr': 'PSNR_C, dB',
    'container ssim': 'SSIM_C',
    'watermark psnr': 'PSNR_W, dB',
    'watermark ssim': 'SSIM_C',
    'watermark bcr':  'BCR',
    'container bpp':  'BPP',
    'key size':       'Размер ключа, байт'
}