import openpyxl
from openpyxl.utils import (get_column_letter)

first_col = 1
first_row = 1


def save_de_results(file, def_params, new_params, def_metrics, new_metrics):
    try:
        workbook = openpyxl.load_workbook(file, guess_types=True)
    except:
        workbook = openpyxl.Workbook()
        workbook.guess_types = True

    issue = def_params["issue"]
    def_params = __prepare_params(def_params)
    new_params = __prepare_params(new_params)
    def_metrics = __prepare_params(def_metrics)
    new_metrics = __prepare_params(new_metrics)

    try:
        sheet = workbook.get_sheet_by_name("issue " + str(issue))
    except:
        sheet = workbook.create_sheet("issue " + str(issue))
        headers = (*def_params["headers"], *def_metrics["headers"], *new_params["headers"], *new_metrics["headers"])
        past_list_in_row(sheet, first_col, first_row, headers)

    row = first_row + 1
    container = def_params["values"][0]
    watermark = def_params["values"][1]
    while True:
        container_cell_val = sheet[cell(first_col, row)].value
        watermark_cell_val = sheet[cell(first_col + 1, row)].value
        if container_cell_val is None:
            break
        if container_cell_val == container and watermark_cell_val == watermark:
            break
        row += 1

    values = (*def_params["values"], *def_metrics["values"], *new_params["values"], *new_metrics["values"])
    past_list_in_row(sheet, first_col, row, values)
    workbook.save(file)


def cell(col, row):
    return get_column_letter(col) + str(row)


def cells_range(col1, row1, col2, row2):
    return cell(col1, row1) + ":" + cell(col2, row2)


def __prepare_params(params):
    headers = []
    values = []
    if "container" in params:
        headers.append("Container")
        values.append(params['container'].split("\\")[-1].split(".")[0])
    if "watermark" in params:
        headers.append("Watermark")
        values.append(params['watermark'].split("\\")[-1].split(".")[0])
    if "homogeneity_threshold" in params:
        th = params["homogeneity_threshold"]
        if isinstance(th, (tuple, list)):
            headers.extend("th" + str(i) for i in range(1, len(th) + 1))
            values.extend(th)
        else:
            headers.append("th")
            values.append(th)
    if "min_block_size" in params and "max_block_size" in params:
        headers.extend(("min", "max"))
        values.extend((params["min_block_size"], params["max_block_size"]))
    if "quant_power" in params:
        headers.append("qp")
        values.append(params["quant_power"])
    if "ch_scale" in params:
        headers.append("scale")
        values.append(params["ch_scale"])
    if "offset" in params:
        headers.extend(("x", "y"))
        values.extend((params["offset"][0], params["offset"][1]))
    if "container psnr" in params:
        headers.append("CONTAINER PSNR")
        values.append(params["container psnr"])
    if "container ssim" in params:
        headers.append("CONTAINER SSIM")
        values.append(params["container ssim"])
    if "watermark psnr" in params:
        headers.append("WATERMARK PSNR")
        values.append(params["watermark psnr"])
    if "watermark ssim" in params:
        headers.append("WATERMARK SSIM")
        values.append(params["watermark ssim"])
    if "watermark bcr" in params:
        headers.append("WATERMARK BCR")
        values.append(params["watermark bcr"])
    if "container bpp" in params:
        headers.append("BPP")
        values.append(params["container bpp"])

    return {
        "headers": headers,
        "values": values
    }


def past_list_in_row(sheet, col, row, list):
    for item in list:
        sheet[cell(col, row)] = item
        col += 1
    return col

