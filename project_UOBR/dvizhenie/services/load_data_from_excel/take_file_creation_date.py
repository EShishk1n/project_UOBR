from datetime import datetime
from os.path import getmtime


def take_file_creation_date() -> str | None:
    """Получает дату создания файла, если файла нет, возвращает None"""

    try:
        return datetime.fromtimestamp(getmtime('dvizhenie/uploads/Движение_БУ.xlsx')).strftime(
            '%d-%m-%Y, %H:%M')
    except FileNotFoundError:
        return None
