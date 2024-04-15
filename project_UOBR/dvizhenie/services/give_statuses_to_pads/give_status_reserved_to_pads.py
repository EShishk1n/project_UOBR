from django.db.models import QuerySet

from dvizhenie.models import NextPosition, Pad
from dvizhenie.services.give_statuses_to_pads.common_function import give_status_to_pads, convert_from_QuerySet_to_list


def give_status_reserved_to_pads() -> None:
    """Присваиваем статус 'reserved' всем кустам, на которые запланировано движение буровой (забронированным)"""

    reserved_pads_QuerySet = get_reserved_pads()
    reserved_pads_list = convert_from_QuerySet_to_list(reserved_pads_QuerySet)
    give_status_to_pads(list_of_pads=reserved_pads_list, status='reserved')


def get_reserved_pads() -> QuerySet(Pad):
    """Получаем список кустов, на которые запланировано движение буровой (забронированных)"""

    reserved_pads = NextPosition.objects.filter(status__in=['commited', 'changed']).values_list('next_position')

    return reserved_pads
