from django.db.models import QuerySet

from dvizhenie.models import NextPosition


def define_sequence_of_objs_in_NextPosition() -> list:
    """Сортирует объекты в NextPosition по приоритетности определения"""

    objs_from_NextPositions = get_objs_from_NextPosition()

    sequence_of_objs_in_NextPosition = define_sequence(objs_from_NextPositions)

    return sequence_of_objs_in_NextPosition


def get_objs_from_NextPosition() -> QuerySet(NextPosition):

    status_to_exclude = ['commited', 'deleted', 'changed']
    objs_from_NextPosition = (
        NextPosition.objects.exclude(status__in=status_to_exclude).order_by('current_position__end_date'))

    return objs_from_NextPosition


def define_sequence(objs: QuerySet(NextPosition)) -> list:

    light_rigs = []
    less_than_middle_rigs = []
    middle_rigs = []
    less_than_heavy_rigs = []
    ZJ = []
    SNPH_rigs = []
    other_rigs = []

    for obj in objs:
        capacity = int(obj.current_position.drilling_rig.capacity())
        type_of_DR = str(obj.current_position.drilling_rig.type)
        contractor = str(obj.current_position.drilling_rig.contractor)

        if capacity == 200:
            light_rigs.append(obj)
        elif capacity == 225:
            less_than_middle_rigs.append(obj)
        elif capacity == 250:
            middle_rigs.append(obj)
        elif capacity == 270:
            less_than_heavy_rigs.append(obj)
        elif type_of_DR == 'ZJ-50 0.5эш':
            ZJ.append(obj)
        else:
            if contractor == 'СНПХ':
                SNPH_rigs.append(obj)
            else:
                other_rigs.append(obj)

    return light_rigs + less_than_middle_rigs + ZJ + middle_rigs + less_than_heavy_rigs + SNPH_rigs + other_rigs
