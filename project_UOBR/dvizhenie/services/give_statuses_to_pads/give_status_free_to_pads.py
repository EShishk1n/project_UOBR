from django.db.models import QuerySet

from dvizhenie.models import Pad
from dvizhenie.services.give_statuses_to_pads.common_function import give_status_to_pads, convert_from_QuerySet_to_list


def give_status_free_to_pads() -> None:
    """Присваиваем статус 'free' всем не отбуренным и не забронированным кустам, кустам не в бурении"""

    free_pads_Queryset = get_free_pads_id()
    free_pads_list = convert_from_QuerySet_to_list(free_pads_Queryset)
    give_status_to_pads(list_of_pads=free_pads_list, status='free')


def get_free_pads_id() -> QuerySet(Pad):
    """Получаем все не отбуренные и не забронированные кусты (кусты в бурении)"""

    free_pads = Pad.objects.exclude(status__in=['drilled', 'drilling', 'reserved']).values_list('id')

    return free_pads
