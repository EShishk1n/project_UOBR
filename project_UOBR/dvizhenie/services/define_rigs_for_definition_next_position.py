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


def form_next_position(start_date_for_calculation, end_date_for_calculation) -> None:
    """Формирует данные в модели NextPosition"""

    status_to_exclude = ['Подтверждено', 'Изменено. Требуется подтверждение', 'Удалено пользователем']
    NextPosition.objects.exclude(status__in=status_to_exclude).delete()
    _put_rigs_for_define_in_NextPosition(start_date_for_calculation, end_date_for_calculation)


def _put_rigs_for_define_in_NextPosition(start_date_for_calculation, end_date_for_calculation) -> None:
    """Вставляет в модель NextPosition, после проверки на наличие в модели,
    буровые установки для определения движения"""

    rigs_for_define_next_position: [QuerySet] = _get_rigs_for_calculation_rating(start_date_for_calculation,
                                                                                 end_date_for_calculation)

    rigs_for_define_next_position_already_in_model: [QuerySet] = NextPosition.objects.all().values_list(
        'current_position')

    for rig_for_define_next_position in rigs_for_define_next_position:
        if (rig_for_define_next_position.id,) not in rigs_for_define_next_position_already_in_model:
            NextPosition(current_position=rig_for_define_next_position).save()


def _get_rigs_for_calculation_rating(start_date_for_calculation: datetime.date,
                                     end_date_for_calculation: datetime.date) -> QuerySet:
    """Получает список буровых установок, которые выйдут из бурения в течении определенного периода"""

    _get_status_to_pads()

    return (RigPosition.objects.filter(end_date__range=(start_date_for_calculation, end_date_for_calculation)) &
            RigPosition.objects.filter(pad__status='drilling').order_by('end_date'))


def _get_status_to_pads() -> None:
    """Присваивает статус 'в бурении/пробурен' кустам"""

    # Поучаем список всех буровых в RigPosition, которые упоминаются более 1 раза ( = уже переезжали)
    rig_positions_id = []
    for rig_position_id in RigPosition.objects.exclude(pad__status='drilled').values_list('drilling_rig__id'):
        rig_positions_id.append(rig_position_id[0])

    counter = Counter(rig_positions_id)
    dislocated_drilling_rigs = list(key for key in counter if counter[key] > 1)

    # Поучаем список всех отбуренных кустов и обновляем статус drilled в Pad
    drilled_pads_id = []

    for dislocated_drilling_rig in dislocated_drilling_rigs:
        drilled_pads_id.append(
            RigPosition.objects.filter(drilling_rig__id=dislocated_drilling_rig).values_list('pad')[0][0])

    Pad.objects.filter(id__in=drilled_pads_id).update(status='drilled')

    # Поучаем список всех кустов, на которых стоят буровые ( = все элементы, кроме статуса 'drilled')
    drilling_pads_id = []
    for drilling_and_drilled_pad_id in RigPosition.objects.exclude(pad__status='drilled').values_list('pad'):
        drilling_pads_id.append(drilling_and_drilled_pad_id[0])

    # Получаем список кустов на которые подтверждено движение буровой установки
    commited_next_position_pads = []
    for commited_next_position_pad in NextPosition.objects.filter(status='Подтверждено').values_list('next_position'):
        commited_next_position_pads.append(commited_next_position_pad[0])

    # Получаем список кустов на который выбрано движение "вручную"
    changed_next_position_pads = []
    for changed_next_position_pad in NextPosition.objects.filter(
            status='Изменено. Требуется подтверждение').values_list('next_position'):
        changed_next_position_pads.append(changed_next_position_pad[0])

    # Обновляем статусы в Pad
    Pad.objects.filter(id__in=drilling_pads_id).update(status='drilling')
    Pad.objects.filter(id__in=commited_next_position_pads).update(status='commited_next_positions')
    Pad.objects.filter(id__in=changed_next_position_pads).update(status='changed_next_positions')
