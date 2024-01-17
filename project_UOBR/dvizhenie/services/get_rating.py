from django.db.models import QuerySet
from dvizhenie.models import RigPosition, Pad, PositionRating

from datetime import date, timedelta
from .dop_inf import for_m_e_rating

def get_ratings_and_put_into_BD() -> None:
    """Получает рейтинг для каждой пары буровая установка-куст"""

    free_pads = _get_free_pads()
    rigs_for_define_next_position = _get_rigs_for_define_next_position()

    for rig_for_define_next_position in rigs_for_define_next_position:
        for free_pad in free_pads:
            _get_rating_and_put_into_BD(rig_for_define_next_position, free_pad)


def _get_free_pads() -> list:
    """Получает список свободных кустов"""

    free_pads = []
    booked_pads = list(RigPosition.objects.all().values_list('pad'))
    all_the_pads = Pad.objects.all()
    for pad in all_the_pads:
        if (pad.id,) not in booked_pads:
            free_pads.append(pad)
    return free_pads


def _get_rigs_for_define_next_position() -> QuerySet:
    """Получает список буровых установок, которые выйдут из бурения в течении следующих 3 месяцев, для определения
    последующего движения"""

    month_for_defenition = date.today().month
    return RigPosition.objects.filter(end_date__month__range=(month_for_defenition, int(month_for_defenition) + 3))


def _get_rating_and_put_into_BD(rig_for_define_next_position: RigPosition, free_pad: Pad) -> None:
    """Получает рейтинг для пары кустов и отправляет его в БД"""

    current_position_end_date = rig_for_define_next_position.end_date

    capacity_rating = _get_capacity_rating(rig_for_define_next_position, free_pad)
    first_stage_date_rating = _get_first_stage_date_rating(rig_for_define_next_position, free_pad)
    second_stage_date_rating = _get_second_stage_date_rating(rig_for_define_next_position, free_pad)
    mud_rating = _get_mud_rating(rig_for_define_next_position, free_pad)
    logistic_rating = _get_logistic_rating(rig_for_define_next_position, free_pad)
    marker_rating = _get_marker_rating(rig_for_define_next_position, free_pad)
    strategy_rating = _get_strategy_rating(rig_for_define_next_position, free_pad)

    if (capacity_rating * first_stage_date_rating * second_stage_date_rating * mud_rating * logistic_rating
            * marker_rating * strategy_rating == 0):
        pass

    else:
        common_rating = (
                capacity_rating * 2.5 + first_stage_date_rating * 1.5 + second_stage_date_rating * 0.7 + mud_rating * 1
                + logistic_rating * 3 + marker_rating * 0.1 + strategy_rating * 1.2)

        ratings = PositionRating(current_position=rig_for_define_next_position,
                                 current_position_end_date=current_position_end_date, next_position=free_pad,
                                 capacity_rating=capacity_rating, first_stage_date_rating=first_stage_date_rating,
                                 second_stage_date_rating=second_stage_date_rating, mud_rating=mud_rating,
                                 logistic_rating=logistic_rating, marker_rating=marker_rating,
                                 strategy_rating=strategy_rating, common_rating=common_rating)

        ratings.save()


def _get_capacity_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
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

    elif (
            rig_capacity == 320 and required_capacity == 400 or
            rig_capacity == 270 and required_capacity == 320 or
            rig_capacity == 250 and required_capacity == 270 or
            rig_capacity == 225 and required_capacity == 250 or
            rig_capacity == 200 and required_capacity == 225):
        capacity_rating = 0.5

    else:
        capacity_rating = 0

    return capacity_rating


def _get_first_stage_date_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг по дате готовности первого этапа для пары кустов"""

    end_date = rig_for_define_next_position.end_date
    first_stage_date = free_pad.first_stage_date

    if end_date >= first_stage_date:
        first_stage_date_rating = 10

    # Первый этап будет готов через 7 дней после выхода БУ (9 баллов)
    elif end_date + timedelta(7) >= first_stage_date:
        first_stage_date_rating = 9

    # Первый этап будет готов через 12 дней после выхода БУ (8 баллов)
    elif end_date + timedelta(12) >= first_stage_date:
        first_stage_date_rating = 8

    # Первый этап будет готов через 18 дней после выхода БУ (3 баллов)
    elif end_date + timedelta(18) >= first_stage_date:
        first_stage_date_rating = 3

    # Первый этап будет готов через 20 дней после выхода БУ (1 балл, требуется ускорение)
    elif end_date + timedelta(20) >= first_stage_date:
        first_stage_date_rating = 1

    else:
        first_stage_date_rating = 0

    return first_stage_date_rating


def _get_second_stage_date_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
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


def _get_mud_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
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
        mud_rating = 9

    else:
        mud_rating = 0

    return mud_rating


def _get_logistic_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг по логистике для пары кустов"""

    rig_field = str(rig_for_define_next_position.pad.field)
    pad_field = str(free_pad.field)

    combination_for_geting_rating = rig_field + pad_field
    logistic_rating = for_m_e_rating[combination_for_geting_rating]

    return logistic_rating


def _get_marker_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Определяет рейтинг для нетиповых случаев (нестандартная буровая установка, буровой подрядчик - СНПХ,
    приоритетное бурение кустовой площадки"""

    rig_type = str(rig_for_define_next_position.drilling_rig.type)
    rig_contractor = str(rig_for_define_next_position.drilling_rig.contractor)
    marker = str(free_pad.marker)

    if rig_type == 'ZJ-50 2эш':
        if marker == 'для 2эш':
            marker_rating = 10
        else:
            marker_rating = 0

    elif rig_type == 'ZJ-50 0.5эш':
        if free_pad.gs_quantity + free_pad.nns_quantity <= 8:
            marker_rating = 10
        else:
            marker_rating = 0

    elif rig_contractor == "СНПХ":
        if marker == 'СНПХ':
            marker_rating = 10
        else:
            marker_rating = 0

    elif marker == 'приоритет':
        marker_rating = 10

    else:
        marker_rating = 1

    return marker_rating


def _get_strategy_rating(rig_for_define_next_position: RigPosition, free_pad: Pad) -> float:
    """Получает рейтинг соответствия стратегии"""

    rig_contractor = str(rig_for_define_next_position.drilling_rig.contractor)
    current_field = str(rig_for_define_next_position.pad.field)
    next_field = str(free_pad.field)

    if rig_contractor == 'НФ РНБ':
        # Первый УБР на ПРО
        if current_field in ['ПРОл', 'ПРОп'] and next_field in ['ПРОл', 'ПРОп', 'ПРЗ', 'САЛ']:
            strategy_rating = 10

        # Второй УБР на Правдинском регионе
        elif current_field in ['ПРЗ', 'САЛ'] and next_field in ['ПРЗ', 'САЛ']:
            strategy_rating = 10

        # Третий УБР на Юганском и Майском регионе
        elif (current_field not in ['ПРОл', 'ПРОп', 'ПРЗ', 'САЛ']
              and next_field not in ['ПРОл', 'ПРОп', 'ПРЗ', 'САЛ', 'ЭРГ']):
            strategy_rating = 10
        else:
            strategy_rating = 1

    elif rig_contractor == 'ХМФ РНБ':
        # Первый УБР на ПРО
        if current_field in ['ПРОл', 'ПРОп', 'ПРЗ', 'САЛ'] and next_field in ['ПРОл', 'ПРОп']:
            strategy_rating = 10

        # Четвертный УБР на Юганском, Майском, Правдинском регионе
        elif current_field not in ['ПРОл', 'ПРОп', 'ПРЗ', 'САЛ'] and next_field not in ['ПРОл', 'ПРОп']:
            strategy_rating = 10
        else:
            strategy_rating = 1

    elif rig_contractor in ['НвФ РНБ', 'СНПХ', 'ГПБ', 'ТБНГ', 'КСА', 'МУБР']:
        strategy_rating = 10

    else:
        strategy_rating = 1

    return strategy_rating
