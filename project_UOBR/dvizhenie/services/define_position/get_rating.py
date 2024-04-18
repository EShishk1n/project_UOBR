from dvizhenie.models import RigPosition, Pad, PositionRating

from datetime import timedelta
from .dop_inf import rating_of_moving_between_fields


def get_rating_and_put_into_DB(rig_for_define_next_position: RigPosition, free_pad: Pad) -> None:
    """Получает рейтинг для пары кустов и отправляет его в БД"""

    rating = get_rating(rig_for_define_next_position, free_pad)

    if type(rating) is PositionRating:
        rating.save()


def get_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> PositionRating:
    """Получает рейтинг для пары кустов"""

    rating = PositionRating(current_position=rig_for_define_next_position,
                            next_position=free_pad,
                            capacity_rating=get_capacity_rating(rig_for_define_next_position, free_pad),
                            first_stage_date_rating=get_first_stage_date_rating(rig_for_define_next_position, free_pad),
                            second_stage_date_rating=get_second_stage_date_rating(rig_for_define_next_position,
                                                                                  free_pad),
                            mud_rating=get_mud_rating(rig_for_define_next_position, free_pad),
                            logistic_rating=get_logistic_rating(rig_for_define_next_position, free_pad),
                            marker_rating=get_marker_rating(rig_for_define_next_position, free_pad))

    if (rating.capacity_rating * rating.first_stage_date_rating * rating.second_stage_date_rating *
            rating.mud_rating * rating.logistic_rating * rating.marker_rating != 0):
        rating.common_rating = rating.calculate_common_rating()

        return rating


def get_capacity_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг по грузоподъемности для пары кустов"""

    rig_capacity = int(rig_for_define_next_position.drilling_rig.capacity())
    required_capacity = int(free_pad.required_capacity)

    if rig_capacity == required_capacity:
        capacity_rating = 10

    elif (rig_capacity == 400 and required_capacity == 320 or
          rig_capacity == 320 and required_capacity == 270 or
          rig_capacity == 270 and required_capacity == 250 or
          rig_capacity == 250 and required_capacity == 225 or
          rig_capacity == 225 and required_capacity == 200):
        capacity_rating = 8

    elif (rig_capacity == 400 and required_capacity == 270 or
          rig_capacity == 320 and required_capacity == 250 or
          rig_capacity == 270 and required_capacity == 225 or
          rig_capacity == 250 and required_capacity == 225):
        capacity_rating = 3

    elif (rig_capacity == 400 and required_capacity == 250 or
          rig_capacity == 320 and required_capacity == 225 or
          rig_capacity == 270 and required_capacity == 200 or
          rig_capacity == 250 and required_capacity == 200):
        capacity_rating = 1

    else:
        capacity_rating = 0

    return capacity_rating


def get_first_stage_date_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг по дате готовности первого этапа для пары кустов"""

    end_date = rig_for_define_next_position.end_date
    first_stage_date = free_pad.first_stage_date

    if end_date >= first_stage_date:
        first_stage_date_rating = 10

    # Первый этап будет готов через 7 дней после выхода БУ (9 баллов)
    elif end_date + timedelta(7) >= first_stage_date:
        first_stage_date_rating = 9

        # Первый этап будет готов через 12 дней после выхода БУ (6 баллов)
    elif end_date + timedelta(12) >= first_stage_date:
        first_stage_date_rating = 6

    # Первый этап будет готов через 18 дней после выхода БУ (1 баллов)
    elif end_date + timedelta(18) >= first_stage_date:
        first_stage_date_rating = 1

    # Первый этап будет готов через 25 дней после выхода БУ (0.5 баллов)
    elif end_date + timedelta(25) >= first_stage_date:
        first_stage_date_rating = 0.5

    else:
        first_stage_date_rating = 0

    return first_stage_date_rating


def get_second_stage_date_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг по дате готовности второго этапа для пары кустов"""

    end_date = rig_for_define_next_position.end_date
    second_stage_date = free_pad.second_stage_date

    # Второй этап будет готов через 14 дней после выхода БУ (10 баллов)
    if end_date + timedelta(14) >= second_stage_date:
        second_stage_date_rating = 10

    # Второй этап будет готов через 21 дней после выхода БУ (7 баллов)
    elif end_date + timedelta(21) >= second_stage_date:
        second_stage_date_rating = 7

    # Второй этап будет готов через 28 дней после выхода БУ (4 балла)
    elif end_date + timedelta(28) >= second_stage_date:
        second_stage_date_rating = 4

    # Второй этап будет готов через 42 дня после выхода БУ (1 балл, требуется ускорение)
    elif end_date + timedelta(42) >= second_stage_date:
        second_stage_date_rating = 0.5

    else:
        second_stage_date_rating = 0

    return second_stage_date_rating


def get_mud_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг по типу бурового раствора для пары кустов"""

    mud = str(rig_for_define_next_position.drilling_rig.mud)
    required_mud = str(free_pad.required_mud)

    # используемый тип БР соответствует требуемому
    if mud == required_mud:
        mud_rating = 10

    # Модернизироанная под РУО буровая едет на куст не РУО
    elif mud == 'РВО' and required_mud == 'РУО' and free_pad.gs_quantity != 0:
        if free_pad.gs_quantity <= 6 and free_pad.nns_quantity / free_pad.gs_quantity >= 2.5:
            mud_rating = 10
        else:
            mud_rating = 5

    elif mud == 'РУО' and required_mud == 'РВО':
        mud_rating = 4

    else:
        mud_rating = 0

    return mud_rating


def get_logistic_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг по логистике для пары кустов"""

    rig_field = str(rig_for_define_next_position.pad.field)
    pad_field = str(free_pad.field)

    combination_for_geting_rating = rig_field + pad_field
    logistic_rating = rating_of_moving_between_fields[combination_for_geting_rating]

    return logistic_rating


def get_marker_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Определяет рейтинг для нетиповых случаев (нестандартная буровая установка, буровой подрядчик - СНПХ,
    приоритетное бурение кустовой площадки"""

    marker_for_drilling_rig = get_marker_for_drilling_rig(rig_for_define_next_position)
    marker_for_pad = str(free_pad.marker)

    if marker_for_drilling_rig == 'стандартная БУ':
        if marker_for_pad == 'для 2эш':
            marker_rating = 0
        elif marker_for_pad == 'СНПХ':
            marker_rating = 4
        else:
            marker_rating = 10

    elif marker_for_drilling_rig == 'СНПХ':
        if marker_for_pad == 'СНПХ':
            marker_rating = 10
        else:
            marker_rating = 0

    elif marker_for_pad == 'для 2эш':
        if marker_for_drilling_rig == 'ZJ-50 2эш':
            marker_rating = 10
        else:
            marker_rating = 0

    elif marker_for_drilling_rig == 'ZJ-50 0.5эш':
        if free_pad.gs_quantity + free_pad.nns_quantity <= 8:
            marker_rating = 10
        else:
            marker_rating = 0

    elif marker_for_pad == 'приоритет':
        marker_rating = 10

    else:
        marker_rating = 0

    return marker_rating


def get_marker_for_drilling_rig(rig_for_define_next_position: RigPosition) -> str:
    """Получает информацию о маркере буровой установки"""

    rig_type = str(rig_for_define_next_position.drilling_rig.type)
    rig_contractor = str(rig_for_define_next_position.drilling_rig.contractor)

    if rig_type in ('ZJ-50 2эш', 'ZJ-50 0.5эш'):
        marker_for_rig_position = rig_type

    elif rig_contractor == 'СНПХ':
        marker_for_rig_position = rig_contractor

    else:
        marker_for_rig_position = 'стандартная БУ'

    return marker_for_rig_position
