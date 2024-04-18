from openpyxl.reader.excel import load_workbook


def open_work_sheet(filename: str):
    """Открывает файл. Нужна для искючения ошибки при запуске сайта при отсутствии файла в папке"""

    wb = load_workbook(filename=filename)

    return wb['Движение_БУ']
