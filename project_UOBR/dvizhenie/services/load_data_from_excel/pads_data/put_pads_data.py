from dvizhenie.models import Pad
from dvizhenie.services.define_position.dop_inf import fields
from dvizhenie.services.load_data_from_excel.pads_data.take_pads_data import take_pads_data_from_table


def put_pads_data(table_start_row: int, table_end_row: int, path: str):
    """Вставляет данные, полученные из таблицы в модель Pad"""

    pads_data = take_pads_data_from_table(table_start_row=table_start_row, table_end_row=table_end_row, path=path)

    for pad_data in pads_data:
        pad_already_in_Pad = Pad.objects.filter(number=pad_data['number'], field=pad_data['field'])

        if pad_already_in_Pad:
            update_Pad_object(pad_already_in_Pad[0], pad_data)

        elif pad_data['field'] in fields:
            create_Pad_object(pad_data)

        else:
            return {'pad_data': pad_data, 'error_message': 'Такого месторождения нет в перечне'}


def update_Pad_object(pad_already_in_Pad: Pad, pad_data: dict) -> None:

    Pad.objects.filter(id=pad_already_in_Pad.id).update(first_stage_date=pad_data['first_stage_date'],
                                                        second_stage_date=pad_data['second_stage_date'],
                                                        required_capacity=pad_data['required_capacity'],
                                                        required_mud=pad_data['required_mud'],
                                                        gs_quantity=pad_data['gs_quantity'],
                                                        nns_quantity=pad_data['nns_quantity'],
                                                        marker=pad_data['marker'])


def create_Pad_object(pad_data: dict) -> None:

    Pad(number=pad_data['number'],
        field=pad_data['field'],
        first_stage_date=pad_data['first_stage_date'],
        second_stage_date=pad_data['second_stage_date'],
        required_capacity=pad_data['required_capacity'],
        required_mud=pad_data['required_mud'],
        gs_quantity=pad_data['gs_quantity'],
        nns_quantity=pad_data['nns_quantity'],
        marker=pad_data['marker']).save()
