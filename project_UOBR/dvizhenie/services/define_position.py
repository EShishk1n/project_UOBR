from dvizhenie.models import PositionRating, NextPosition
from .get_rating import _get_rigs_for_define_next_position, get_ratings_and_put_into_BD


def define_position_and_put_into_BD() -> None:
    """Определяет следующую позицию для БУ по максимальному рейтингу и отправляет данные в БД"""

    _clear_work_tables()

    get_ratings_and_put_into_BD()

    rigs_for_define_next_position = _get_rigs_for_define_next_position()

    for rig_for_define_next_position in rigs_for_define_next_position:
        positions = list(PositionRating.objects.filter(current_position=rig_for_define_next_position)
                         .order_by('-common_rating') & PositionRating.objects.filter(status=''))
        if not positions:
            NextPosition(current_position=rig_for_define_next_position, status='Отсутствют кандидаты').save()

        else:
            position = positions[0].next_position

            PositionRating.objects.filter(next_position=position).update(status='booked')
            if float(positions[0].common_rating) >= 50:
                NextPosition(current_position=rig_for_define_next_position, next_position=position).save()
            else:
                NextPosition(current_position=rig_for_define_next_position, next_position=position,
                             status='необходим ''пересмотр').save()


def _clear_work_tables() -> None:
    """Очищает рабочие таблины (предыдущие расчеты рейтинга и определения движения)"""

    NextPosition.objects.all().delete()
    PositionRating.objects.all().delete()
