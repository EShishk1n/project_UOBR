from dvizhenie.services.load_data_from_excel.open_work_sheet import open_work_sheet


def take_pads_data_from_table(table_start_row: int, table_end_row: int, path: str) -> list:
    """Имортирует данные по КП из файла 'Движение_БУ'"""

    sheet = open_work_sheet(path)

    min_row = table_start_row
    max_row = table_end_row
    min_col = 9
    max_col = 19

    pads_data = []

    for row in sheet.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col, values_only=True):
        pad_data = take_pads_data_from_row(row)
        pads_data.append(pad_data)

    return pads_data


def take_pads_data_from_row(row: tuple) -> dict:

    if row[0] is not None:
        marker_data = take_marker_data_from_row(row)
        pad_data = {'number': row[0],
                    'field': row[1],
                    'first_stage_date': row[2].date(),
                    'second_stage_date': row[3].date(),
                    'required_capacity': row[5],
                    'required_mud': row[6],
                    'marker': marker_data,
                    'gs_quantity': row[10],
                    'nns_quantity': row[9] - row[10]
                    }

        return pad_data


def take_marker_data_from_row(row: tuple) -> str:

    if row[8] is None:
        marker_data = 'нет'
    else:
        marker_data = row[8]

    return marker_data
