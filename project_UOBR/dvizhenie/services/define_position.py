import datetime

from dvizhenie.models import PositionRating, NextPosition, RigPosition, Pad
from .calculate_all_ratings_and_put_into_DB import calculate_all_ratings_and_put_into_DB
from .define_rigs_for_definition_next_position import define_sequence_of_rigs_for_definition_positions, form_next_position


def define_position_and_put_into_BD(start_date_for_calculation: datetime.date,
                                    end_date_for_calculation: datetime.date) -> None:
    """Определяет следующую позицию для БУ по максимальному рейтингу и отправляет данные в БД"""

    PositionRating.objects.all().delete()

    calculate_all_ratings_and_put_into_DB(start_date_for_calculation,
                                          end_date_for_calculation)

    form_next_position(start_date_for_calculation, end_date_for_calculation)

    rigs_for_define_next_position: [list] = define_sequence_of_rigs_for_definition_positions()

    for rig_for_define_next_position in rigs_for_define_next_position:
        result: [dict] = _define_next_position(rig_for_define_next_position.current_position)

        NextPosition.objects.filter(current_position=rig_for_define_next_position.current_position).update(
            status=result['status'])
        NextPosition.objects.filter(current_position=rig_for_define_next_position.current_position).update(
            next_position=result['next_position'])







def _define_next_position(rig_for_define_next_position: RigPosition) -> dict:
    """Определяет следующую позицию для одной буровой установки. Присваивает статус паре"""

    positions = PositionRating.objects.filter(current_position=rig_for_define_next_position, status='').order_by(
        '-common_rating')

    if not positions:
        next_position = None
        status = 'Отсутствуют кандидаты'

    else:
        next_position = positions.first().next_position
        status = 'Требуется подтверждение'
        PositionRating.objects.filter(next_position=next_position).update(status='booked')

        if next_position.id in NextPosition.objects.all().values('next_position'):
            _define_next_position(rig_for_define_next_position)

    return {'next_position': next_position, 'status': status}
