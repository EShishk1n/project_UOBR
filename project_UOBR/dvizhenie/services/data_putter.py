from dvizhenie.models import Pad, RigPosition
from dvizhenie.services.data_taker import take_rigs_position_data, take_pads_data


def put_rigs_position_data(table_start_row: int, table_end_row: int):
    """Вставляет данные, полученные из таблицы в модель RigPosition"""

    rigs_position_data = take_rigs_position_data(table_start_row=table_start_row, table_end_row=table_end_row)

    for rig_position_data in rigs_position_data:
        drilling_pad = (Pad.objects.filter(number=rig_position_data['number']) &
                        Pad.objects.filter(field=rig_position_data['field']))
        RigPosition.objects.filter(pad=drilling_pad[0].id).update(end_date=rig_position_data['end_date'])


def put_pads_data(table_start_row: int, table_end_row: int):
    """Вставляет данные, полученные из таблицы в модель Pad"""

    pads_data = take_pads_data(table_start_row=table_start_row, table_end_row=table_end_row)

    for pad_data in pads_data:
        building_pad = (Pad.objects.filter(number=pad_data['number']) &
                        Pad.objects.filter(field=pad_data['field']))
        if building_pad:
            Pad.objects.filter(id=building_pad[0].id).update(first_stage_date=pad_data['first_stage_date'])
            Pad.objects.filter(id=building_pad[0].id).update(second_stage_date=pad_data['second_stage_date'])
            Pad.objects.filter(id=building_pad[0].id).update(required_capacity=pad_data['required_capacity'])
            Pad.objects.filter(id=building_pad[0].id).update(required_mud=pad_data['required_mud'])
            Pad.objects.filter(id=building_pad[0].id).update(gs_quantity=pad_data['gs_quantity'])
            Pad.objects.filter(id=building_pad[0].id).update(nns_quantity=pad_data['nns_quantity'])
            Pad.objects.filter(id=building_pad[0].id).update(marker=pad_data['marker'])

        else:
            Pad(number=pad_data['number'],
                field=pad_data['field'],
                first_stage_date=pad_data['first_stage_date'],
                second_stage_date=pad_data['second_stage_date'],
                required_capacity=pad_data['required_capacity'],
                required_mud=pad_data['required_mud'],
                gs_quantity=pad_data['gs_quantity'],
                nns_quantity=pad_data['nns_quantity'],
                marker=pad_data['marker']).save()
