from datetime import datetime

from openpyxl.reader.excel import load_workbook

# Здесь нужно будет реализовать выбор файла напрямую через браузер
wb = load_workbook(filename='C:\web_applications\Движение.xlsx')

sheet = wb['Движение_БУ']


def take_rigs_position_data(table_start: str, table_end: str) -> list:
    """Имортирует данные по окончанию бурения для каждой БУ из файла 'Движение_БУ'"""

    min_row = sheet[table_start].row
    max_row = sheet[table_end].row
    min_col = sheet[table_start].column
    max_col = sheet[table_end].column

    rigs_position_data = []

    for row in sheet.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col, values_only=True):
        rig_position_data = {'number': row[0],
                             'field': row[1],
                             'end_date': datetime.date(row[2])}
        rigs_position_data.append(rig_position_data)

    return rigs_position_data


def take_pads_data(table_start: str, table_end: str) -> list:
    """Имортирует данные по КП из файла 'Движение_БУ'"""

    min_row = sheet[table_start].row
    max_row = sheet[table_end].row
    min_col = sheet[table_start].column
    max_col = sheet[table_end].column

    pads_data = []

    for row in sheet.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col, values_only=True):

        if row[0] is not None:
            if row[8] is None:
                marker = 'нет'
            else:
                marker = row[8]
            print(row)
            pad_data = {'number': row[0],
                        'field': row[1],
                        'first_stage_date': datetime.date(row[2]),
                        'second_stage_date': datetime.date(row[3]),
                        'required_capacity': row[5],
                        'required_mud': row[6],
                        'marker': marker,
                        'gs_quantity': row[10],
                        'nns_quantity': row[9] - row[10]
                        }
            pads_data.append(pad_data)

    return pads_data
