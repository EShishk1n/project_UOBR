from itertools import islice

from django.db.models import QuerySet

from dvizhenie.models import NextPosition, RigPosition
from dvizhenie.services.calculate_all_ratings_and_put_into_DB import get_rigs_for_calculation_rating


def form_next_position(start_date_for_calculation, end_date_for_calculation) -> None:
    """Формирует данные в модели NextPosition"""

    status_to_exclude = ['Подтверждено', 'Изменено. Требуется подтверждение', 'Удалено пользователем']
    NextPosition.objects.exclude(status__in=status_to_exclude).delete()

    put_rigs_for_define_in_NextPosition(start_date_for_calculation, end_date_for_calculation)


def put_rigs_for_define_in_NextPosition(start_date_for_calculation, end_date_for_calculation) -> None:
    """Вставляет в модель NextPosition, после проверки на наличие в модели,
    буровые установки для определения движения"""

    rigs_for_put_into_DB = get_rigs_for_put_into_DB(start_date_for_calculation, end_date_for_calculation)

    obj = (NextPosition(current_position=RigPosition.objects.get(id=rig_for_put_into_DB)) for rig_for_put_into_DB in
           rigs_for_put_into_DB)

    NextPosition.objects.bulk_create(list(obj))


def get_rigs_for_put_into_DB(start_date_for_calculation, end_date_for_calculation) -> list:
    rigs_for_define_next_position: [QuerySet] = get_rigs_for_calculation_rating(start_date_for_calculation,
                                                                                end_date_for_calculation)

    rigs_for_put_into_DB = []
    for rig_for_define_next_position in rigs_for_define_next_position:
        if check_availability_of_rig_in_NextPosition(rig_for_define_next_position) is False:
            rigs_for_put_into_DB.append(rig_for_define_next_position.id)

    return rigs_for_put_into_DB


def check_availability_of_rig_in_NextPosition(rig_for_define_next_position) -> bool:
    rigs_for_define_next_position_already_in_model: [QuerySet] = NextPosition.objects.all().values_list(
        'current_position')

    if (rig_for_define_next_position.id,) in rigs_for_define_next_position_already_in_model:
        return True
    else:
        return False
