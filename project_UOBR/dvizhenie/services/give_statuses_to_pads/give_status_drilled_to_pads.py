from collections import Counter

from dvizhenie.models import RigPosition
from dvizhenie.services.give_statuses_to_pads.common_function import give_status_to_pads


def give_status_drilled_to_pads() -> None:
    """Присваиваем статус 'drilled' отбуренным кустам"""

    drilled_pads = get_drilled_pads()
    give_status_to_pads(list_of_pads=drilled_pads, status='drilled')


def get_drilled_pads() -> list:
    """Получаем все отбуренные кусты (кусты на которых стояли буровые)"""

    drilled_rigs_list = get_dislocated_rigs_list()

    drilled_pads = []
    for drilled_rig in drilled_rigs_list:
        drilled_pads.append(RigPosition.objects.filter(drilling_rig__id=drilled_rig).values_list('pad').first()[0])

    return drilled_pads


def get_dislocated_rigs_list() -> list:
    """Поучаем список всех буровых в RigPosition которые встречаются более одного раза (были передислоцированы)"""

    all_rigs_list = get_all_rigs_list()
    dislocated_rigs_list = list(key for key in all_rigs_list if all_rigs_list[key] > 1)

    return dislocated_rigs_list


def get_all_rigs_list() -> dict:
    """Поучаем список всех буровых в RigPosition"""

    rig_positions_id = []
    for rig_position_id in RigPosition.objects.exclude(pad__status='drilled').values_list('drilling_rig__id'):
        rig_positions_id.append(rig_position_id[0])

    return Counter(rig_positions_id)
