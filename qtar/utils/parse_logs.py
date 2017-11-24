from os import listdir
import re

logs = listdir('logs')
logs = [log for log in logs if re.match("de11 cf wmdct [ _.\w]*.log", log)]


def find_filenames(text):
    regex = r".*images\\(.*).png.*images\\(.*).png"
    matches = re.finditer(regex, text)
    firstmatch = next(matches)

    return firstmatch.groups()

def find_defaults(text):
    regex = (r"threshold: *(\d*.\d*)\n"
             r"min - max block sizes: *(\d*) - (\d*)\n"
             r"watermark block size: *(\d*)\n"
             r"quantization power: *(\d*.\d*)\n"
             r"cf grid size: *(\d*)\n"
             r"scale: *(\d*.\d*)\n"
             r"wmdct scale *(\d*.\d*)\n"
             r"offset: *\((\d*), (\d*)\)\n\n"
             r"embedded")

    matches = re.finditer(regex, text)
    firstmatch = next(matches)

    return firstmatch.groups()


def find_metrics(text):
    regex = (r"Metrics:\n"
             r"PSNR container: *(\d*.\d*)\n"
             r"SSIM container: *(\d*.\d*)\n"
             r"PSNR watermark: *(\d*.\d*)\n"
             r"SSIM watermark: *(\d*.\d*)\n"
             r"BPP: *(\d*.\d*)\n"
             r"BCR: *(\d*.\d*)")

    matches = re.finditer(regex, text)
    firstmatch = next(matches)
    secondmatch = next(matches)

    return firstmatch.groups(), secondmatch.groups()


def find_keysize(text):
    regex = (r"\n"
             r"key size: *(\d*)")


    matches = re.finditer(regex, text)
    firstmatch = next(matches)
    secondmatch = next(matches)

    return firstmatch.groups()[0], secondmatch.groups()[0]


def find_new_params(text):
    regex = (r"homogeneity_threshold: *\((\d*.\d*), (\d*.\d*), (\d*.\d*)\)\n"
             r"min_block_size: *(\d*)\n"
             r"cf_grid_size: *(\d*)\n"
             r"wmdct_block_size: *(\d*)")

    matches = re.finditer(regex, text)
    firstmatch = next(matches)

    return firstmatch.groups()


def find_newold_params(text):
    regex = (r"homogeneity_threshold: *(\d*.\d*)\n"
             r"min_block_size: *(\d*)\n"
             r"cf_grid_size: *(\d*)\n"
             r"wmdct_block_size: *(\d*)")

    matches = re.finditer(regex, text)
    firstmatch = next(matches)

    return firstmatch.groups()


for log in logs:
    with open('logs\\' + log) as file:
        log_text = file.read()

        row = []

        wm, container = find_filenames(log_text)
        row.extend((container, wm))

        th, min_b, max_b, wmdct_b, q, cf_g, scale, wmdct_scale, x, y = find_defaults(log_text)
        row.extend((th, min_b, max_b, q, scale, x, y, cf_g, wmdct_b, wmdct_scale))

        def_metrics, new_metrics = find_metrics(log_text)
        psnr_c, ssim_c, psnr_w, ssim_w, bpp, bcr = def_metrics
        row.extend((psnr_c, ssim_c, psnr_w, ssim_w, bcr, bpp))

        def_key, new_key = find_keysize(log_text)
        row.append(def_key)

        try:
            th1, th2, th3, min_b, cf_g, wmdct_b = find_new_params(log_text)
            row.extend((th1, th2, th3, min_b, cf_g, wmdct_b))
        except StopIteration:
            th, min_b, cf_g, wmdct_b = find_newold_params(log_text)
            row.extend((th, th, th, min_b, cf_g, wmdct_b))

        psnr_c, ssim_c, psnr_w, ssim_w, bpp, bcr = new_metrics
        row.extend((psnr_c, ssim_c, psnr_w, ssim_w, bcr, bpp))

        row.append(new_key)

        print(', '.join(row))





