from django.db.models import QuerySet

from dvizhenie.models import Pad


def give_status_to_pads(list_of_pads: list, status: str) -> None:
    Pad.objects.filter(id__in=list_of_pads).update(status=status)


def convert_from_QuerySet_to_list(queryset: QuerySet) -> list:

    res_list = []
    for obj in queryset:
        res_list.append(obj[0])

    return res_list



