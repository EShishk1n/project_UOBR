from collections import Counter
from datetime import datetime

from django.db.models import QuerySet

from dvizhenie.models import RigPosition, Pad, NextPosition


def define_sequence_of_rigs_for_definition_positions() -> list:
    """Определет порядок буровых установок для определения следующей позиции"""

    rigs_for_define_next_position = (
            NextPosition.objects.exclude(status='Подтверждено').order_by('current_position__end_date') &
            NextPosition.objects.exclude(status='Изменено. Требуется подтверждение') &
            NextPosition.objects.exclude(status='Удалено пользователем'))

    light_rigs = []
    less_than_middle_rigs = []
    middle_rigs = []
    less_than_heavy_rigs = []
    ZJ = []
    SNPH_rigs = []
    other_rigs = []

    for rig_for_define_next_position in rigs_for_define_next_position:
        capacity = int(rig_for_define_next_position.current_position.drilling_rig.capacity())
        type_of_DR = str(rig_for_define_next_position.current_position.drilling_rig.type)
        contractor = str(rig_for_define_next_position.current_position.drilling_rig.contractor)

        if capacity == 200:
            light_rigs.append(rig_for_define_next_position)
        elif capacity == 225:
            less_than_middle_rigs.append(rig_for_define_next_position)
        elif capacity == 250:
            middle_rigs.append(rig_for_define_next_position)
        elif capacity == 270:
            less_than_heavy_rigs.append(rig_for_define_next_position)
        elif type_of_DR == 'ZJ-50 0.5эш':
            ZJ.append(rig_for_define_next_position)
        else:
            if contractor == 'СНПХ':
                SNPH_rigs.append(rig_for_define_next_position)
            else:
                other_rigs.append(rig_for_define_next_position)

    return light_rigs + less_than_middle_rigs + ZJ + middle_rigs + less_than_heavy_rigs + SNPH_rigs + other_rigs


