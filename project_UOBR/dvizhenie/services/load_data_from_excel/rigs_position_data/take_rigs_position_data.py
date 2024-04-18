from dvizhenie.services.load_data_from_excel.open_work_sheet import open_work_sheet


def take_rigs_position_data_from_table(table_start_row: int, table_end_row: int) -> list:
    """Имортирует данные по окончанию бурения для каждой БУ из файла 'Движение_БУ'"""

    sheet = open_work_sheet('dvizhenie/uploads/Движение_БУ.xlsx')

    min_row = table_start_row
    max_row = table_end_row
    min_col = 4
    max_col = 6

    rigs_position_data = []

    for row in sheet.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col, values_only=True):
        rig_position_data = take_rigs_position_data_from_row(row)

        rigs_position_data.append(rig_position_data)

    return rigs_position_data


def take_rigs_position_data_from_row(row: tuple) -> dict:
    rig_position_data = {'number': row[0],
                         'field': row[1],
                         'end_date': row[2].date()}

    return rig_position_data
