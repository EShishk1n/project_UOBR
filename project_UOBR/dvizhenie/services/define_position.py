from dvizhenie.models import PositionRating, NextPosition, RigPosition, Pad
from .get_rating import _get_rigs_for_define_next_position, get_ratings_and_put_into_BD


def define_position_and_put_into_BD() -> None:
    """Определяет следующую позицию для БУ по максимальному рейтингу и отправляет данные в БД"""

    PositionRating.objects.all().delete()

    get_ratings_and_put_into_BD()

    rigs_for_define_next_position: [list] = _define_sequence_of_rigs_for_definition_positions()

    for rig_for_define_next_position in rigs_for_define_next_position:
        result: [dict] = _define_next_position(rig_for_define_next_position.current_position)

        NextPosition.objects.filter(current_position=rig_for_define_next_position.current_position).update(
            status=result['status'])
        NextPosition.objects.filter(current_position=rig_for_define_next_position.current_position).update(
            next_position=result['next_position'])

    _define_sequence_of_rigs_for_view()


def _put_rigs_for_define_in_NextPosition() -> None:
    """Вставляет в модель NextPosition,
    после проверки на наличие в модели,
    буровые установки для определения движения"""

    rigs_for_define_next_position = _get_rigs_for_define_next_position()
    rigs_for_define_next_position_already_in_model = NextPosition.objects.all().values_list("current_position")
    for rig_for_define_next_position in rigs_for_define_next_position:
        if (rig_for_define_next_position.id,) not in rigs_for_define_next_position_already_in_model:
            NextPosition(current_position=rig_for_define_next_position).save()


def _define_sequence_of_rigs_for_definition_positions() -> list:
    """Определет порядок буровых установок для определения следующей позиции"""

    _put_rigs_for_define_in_NextPosition()

    rigs_for_define_next_position = (NextPosition.objects.exclude(status='Подтверждено') &
                                     NextPosition.objects.exclude(status='Изменено. Требуется подтверждение'))

    light_rigs = []
    less_than_middle_rigs = []
    middle_rigs = []
    less_than_heavy_rigs = []
    SNPH_rigs = []
    other_rigs = []

    for rig_for_define_next_position in rigs_for_define_next_position:
        capacity = int(rig_for_define_next_position.current_position.drilling_rig.capacity())
        contractor = str(rig_for_define_next_position.current_position.drilling_rig.contractor)

        if capacity == 200:
            light_rigs.append(rig_for_define_next_position)
        elif capacity == 225:
            less_than_middle_rigs.append(rig_for_define_next_position)
        elif capacity == 250:
            middle_rigs.append(rig_for_define_next_position)
        elif capacity == 270:
            less_than_heavy_rigs.append(rig_for_define_next_position)
        else:
            if contractor == 'СНПХ':
                SNPH_rigs.append(rig_for_define_next_position)
            else:
                other_rigs.append(rig_for_define_next_position)

    return light_rigs + less_than_middle_rigs + middle_rigs + less_than_heavy_rigs + SNPH_rigs + other_rigs


def _define_next_position(rig_for_define_next_position: RigPosition) -> dict:
    """Определяет следующую позицию для одной буровой установки. Присваивает статус паре"""

    positions = PositionRating.objects.filter(current_position=rig_for_define_next_position).order_by(
        '-common_rating') & PositionRating.objects.filter(status='')

    if not positions:
        next_position = None
        status = 'Отсутствют кандидаты'

    else:
        next_position = positions.first().next_position
        status = 'Требуется подтверждение'
        PositionRating.objects.filter(next_position=next_position).update(status='booked')

        if {'next_position': next_position.id} in NextPosition.objects.filter(
                status='Изменено. Требуется подтверждение').values('next_position'):
            _define_next_position(rig_for_define_next_position)

    return {'next_position': next_position, 'status': status}


def _define_sequence_of_rigs_for_view() -> None:
    """Определет порядок буровых установок для предоставления"""

    rigs_for_view = NextPosition.objects.all()

    rigs_for_view_dict = {}

    for rig_for_view in rigs_for_view:
        rigs_for_view_dict[rig_for_view] = rig_for_view.current_position.end_date

    sorted_rigs_for_view = sorted(rigs_for_view_dict.items(), key=lambda item: item[1])

    NextPosition.objects.all().delete()

    for rig_for_view in sorted_rigs_for_view:
        NextPosition(current_position=rig_for_view[0].current_position,
                     next_position=rig_for_view[0].next_position,
                     status=rig_for_view[0].status).save()
