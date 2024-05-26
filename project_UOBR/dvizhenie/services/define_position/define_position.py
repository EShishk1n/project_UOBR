import datetime

from django.db.models import QuerySet

from dvizhenie.models import PositionRating, NextPosition, RigPosition, Pad
from .calculate_all_ratings_and_put_into_DB import calculate_all_ratings_and_put_into_DB
from .define_sequence_of_objs_in_NextPosition import define_sequence_of_objs_in_NextPosition
from .form_NextPosition import form_next_position, check_availability_of_obj_in_NextPosition


def define_position_and_put_into_DB(start_date_for_calculation: datetime.date,
                                    end_date_for_calculation: datetime.date) -> None:
    """Определяет следующую позицию для БУ по максимальному рейтингу и отправляет данные в БД"""

    calculate_all_ratings_and_put_into_DB(start_date_for_calculation,
                                          end_date_for_calculation)

    form_next_position(start_date_for_calculation, end_date_for_calculation)

    objs_in_Next_position: [list] = define_sequence_of_objs_in_NextPosition()

    for obj in objs_in_Next_position:
        current_position = obj.current_position
        result: [dict] = define_next_position(current_position)

        put_result_of_definition_in_NextPosition(current_position, result['next_position'], result['status'],
                                                 result['downtime_days'])


def define_next_position(rig_for_define_next_position: RigPosition) -> dict:
    """Определяет следующую позицию для одной буровой установки. Присваивает статус паре"""

    positions = get_objs_from_PositionRating(rig_for_define_next_position)

    if not positions:
        next_position = None
        status = 'empty'
        downtime_days = 100000

    else:
        next_position = positions.first().next_position
        status = 'default'
        downtime_days = positions.first().downtime_days
        give_status_booked_to_PositionRating(next_position)

        if check_availability_of_obj_in_NextPosition(next_position, 'next_position') is True:
            res = define_next_position(rig_for_define_next_position)
            next_position = res['next_position']
            status = res['status']
            downtime_days = res['downtime_days']

    res = {'next_position': next_position, 'status': status, 'downtime_days': downtime_days}

    return res


def get_objs_from_PositionRating(current_position: RigPosition) -> QuerySet(PositionRating):

    objs_from_PositionRating = PositionRating.objects.filter(current_position=current_position, status='').order_by(
        'downtime_days', '-common_rating')

    return objs_from_PositionRating


def give_status_booked_to_PositionRating(booked_next_position: Pad) -> None:

    PositionRating.objects.filter(next_position=booked_next_position).update(status='booked')


def put_result_of_definition_in_NextPosition(current_position: RigPosition, next_position: Pad, status: str,
                                             downtime_days: int) -> None:

    NextPosition.objects.filter(current_position=current_position).update(status=status, next_position=next_position,
                                                                          downtime_days=downtime_days)
