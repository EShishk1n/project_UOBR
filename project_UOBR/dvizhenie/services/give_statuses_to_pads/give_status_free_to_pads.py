from django.db.models import QuerySet

from dvizhenie.models import Pad, NextPosition
from dvizhenie.services.give_statuses_to_pads.common_function import give_status_to_pads, convert_from_QuerySet_to_list
from dvizhenie.services.give_statuses_to_pads.give_status_reserved_to_pads import get_reserved_pads_id


def give_status_free_to_pads() -> None:
    """Присваиваем статус 'free' всем не отбуренным и не забронированным кустам, кустам не в бурении"""

    free_pads_Queryset = get_free_pads_id()
    free_pads_list = convert_from_QuerySet_to_list(free_pads_Queryset)
    give_status_to_pads(list_of_pads=free_pads_list, status='free')


def get_free_pads_id() -> QuerySet(Pad):
    """Получаем все не отбуренные и не забронированные кусты (кусты в бурении)"""

    free_pads = Pad.objects.exclude(status__in=['drilled', 'drilling', 'reserved']).values_list('id')

    return free_pads


def update_status_free_to_pads() -> None:
    """Присваиваем статус 'free' всем кустам, которые ранее были reserved, но сейчас без движения"""
    pads_id_with_status_reserved = set(Pad.objects.filter(status='reserved').values_list('id', flat=True))
    all_next_positions = set(NextPosition.objects.all().values_list('next_position', flat=True))
    pads_with_reserved_status_to_change = pads_id_with_status_reserved - all_next_positions
    Pad.objects.filter(id__in=pads_with_reserved_status_to_change).update(status='free')
