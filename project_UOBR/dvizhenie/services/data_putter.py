from dvizhenie.models import Pad, RigPosition
from dvizhenie.services.data_taker import take_rigs_position_data, take_pads_data


def put_rigs_position_data(table_start_row: int, table_end_row: int):
    """Вставляет данные, полученные из таблицы в модель RigPosition"""

    rigs_position_data = take_rigs_position_data(table_start_row=table_start_row, table_end_row=table_end_row)
    # drilling_pads_in_RigPosition = list(RigPosition.objects.all().values_list('pad__number', 'pad__field'))
    # print(drilling_pads_in_RigPosition)
    for rig_position_data in rigs_position_data:

        drilling_pad = (Pad.objects.filter(number=rig_position_data['number']) &
                        Pad.objects.filter(field=rig_position_data['field']))

        if drilling_pad:
            RigPosition.objects.filter(pad=drilling_pad[0].id).update(end_date=rig_position_data['end_date'])
        else:
            return {'rig_position': rig_position_data, 'error_message': 'Ошибка в наименовании куста'}


def put_pads_data(table_start_row: int, table_end_row: int):
    """Вставляет данные, полученные из таблицы в модель Pad"""

    pads_data = take_pads_data(table_start_row=table_start_row, table_end_row=table_end_row)

    for pad_data in pads_data:
        building_pad = (Pad.objects.filter(number=pad_data['number']) &
                        Pad.objects.filter(field=pad_data['field']))

        if building_pad:
            Pad.objects.filter(id=building_pad[0].id).update(first_stage_date=pad_data['first_stage_date'],
                                                             second_stage_date=pad_data['second_stage_date'],
                                                             required_capacity=pad_data['required_capacity'],
                                                             required_mud=pad_data['required_mud'],
                                                             gs_quantity=pad_data['gs_quantity'],
                                                             nns_quantity=pad_data['nns_quantity'],
                                                             marker=pad_data['marker'])

        elif pad_data['field'] in (
                'ВС', 'ВТК', 'ВПР', 'ВСТР', 'ЕФР', 'ЗУГ', 'КИН', 'КУЗ', 'КУДР', 'МБ', 'МАМ', 'МАЙ', 'МОСК', 'ОМБ',
                'ПЕТ', 'ПРД', 'ПРОп', 'ПРОл', 'ЭРГ', 'ПРЗ', 'САЛ', 'СОЛ', 'СОР', 'СБ', 'СУГ', 'УГ', 'УБ', 'ФН', 'ЮБ',
                'ЮТЕПЛ', 'ЮС',):
            Pad(number=pad_data['number'],
                field=pad_data['field'],
                first_stage_date=pad_data['first_stage_date'],
                second_stage_date=pad_data['second_stage_date'],
                required_capacity=pad_data['required_capacity'],
                required_mud=pad_data['required_mud'],
                gs_quantity=pad_data['gs_quantity'],
                nns_quantity=pad_data['nns_quantity'],
                marker=pad_data['marker']).save()
        else:
            return {'pad_data': pad_data, 'error_message': 'Такого месторождения нет в перечне'}
