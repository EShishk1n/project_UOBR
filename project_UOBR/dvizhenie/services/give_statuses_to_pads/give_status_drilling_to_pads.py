from django.db.models import QuerySet

from dvizhenie.models import RigPosition
from dvizhenie.services.give_statuses_to_pads.common_function import give_status_to_pads, convert_from_QuerySet_to_list


def give_status_drilling_to_pads() -> None:
    """Присваиваем статус 'drilling' всем не отбуренным кустам"""

    drilling_pads_QuerySet = get_drilling_pads()

    drilling_pads_list = convert_from_QuerySet_to_list(drilling_pads_QuerySet)
    give_status_to_pads(list_of_pads=drilling_pads_list, status='drilling')


def get_drilling_pads() -> QuerySet:

    drilling_pads = RigPosition.objects.exclude(pad__status='drilled').values_list('pad')

    return drilling_pads
