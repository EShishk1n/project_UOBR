from dvizhenie.models import Pad, RigPosition
from dvizhenie.services.load_data_from_excel.rigs_position_data.take_rigs_position_data import \
    take_rigs_position_data_from_table


def put_rigs_position_data(table_start_row: int, table_end_row: int):
    """Вставляет данные, полученные из таблицы в модель RigPosition"""

    rigs_position_data = take_rigs_position_data_from_table(table_start_row=table_start_row, table_end_row=table_end_row)

    for rig_position_data in rigs_position_data:

        drilling_pad = Pad.objects.filter(number=rig_position_data['number'], field=rig_position_data['field'])

        if drilling_pad:
            RigPosition.objects.filter(pad=drilling_pad[0].id).update(end_date=rig_position_data['end_date'])
        else:
            return {'rig_position': rig_position_data, 'error_message': 'Ошибка в наименовании куста'}
