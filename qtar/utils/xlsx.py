import openpyxl
from copy import copy
from openpyxl.utils import (get_column_letter)

container_col = 1
watermark_col = 2
headers_row = 1

def save_de_results(file, issue, container, watermark, def_params, new_params):
    try:
        workbook = openpyxl.load_workbook(file, guess_types=True)
    except:
        workbook = openpyxl.Workbook()
        workbook.guess_types = True

    try:
        sheet = workbook.get_sheet_by_name(issue)
    except:
        sheet = workbook.create_sheet(issue)
        sheet[cells_range(container_col, headers_row, watermark_col, headers_row)] = ("Container", "Watermark")
        col = watermark_col + 1
        for name, val in def_params.items():
            if isinstance(val, (tuple, list)):
                




    row = 1
    while True:
        container_cell_val = sheet[cell(container_col, row)].value
        watermark_cell_val = sheet[cell(watermark_col, row)].value
        if container_cell_val is None:
            sheet[cell(container_col, row)] = container
            sheet[cell(watermark_col, row)] = watermark
            break
        if container_cell_val == container and watermark_cell_val == watermark:
            break
        row += 1

    for name, value in def_params:





    workbook.save(file)


def cell(col, row):
    return get_column_letter(col) + str(row)


def cells_range(col1, row1, col2, row2):
    return cell(col1, row1) + ":" + cell(col2, row2)