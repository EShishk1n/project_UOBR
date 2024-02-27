from datetime import date, datetime

from django.db.models import QuerySet

from dvizhenie.models import RigPosition, Pad, PositionRating, NextPosition


def define_sequence_of_rigs_for_definition_positions() -> list:
    """Определет порядок буровых установок для определения следующей позиции"""

    rigs_for_define_next_position = (
            NextPosition.objects.exclude(status='Подтверждено').order_by('current_position__end_date') &
            NextPosition.objects.exclude(status='Изменено. Требуется подтверждение'))

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


def form_next_position() -> None:
    """Формирует данные в модели NextPosition"""

    NextPosition.objects.exclude(status='Подтверждено').delete()
    _put_rigs_for_define_in_NextPosition()


def _put_rigs_for_define_in_NextPosition() -> None:
    """Вставляет в модель NextPosition, после проверки на наличие в модели,
    буровые установки для определения движения"""

    rigs_for_define_next_position: [QuerySet] = PositionRating.objects.all().distinct(
        'current_position').order_by()

    rigs_for_define_next_position_already_in_model: [QuerySet] = NextPosition.objects.all().values_list(
        'current_position')

    for rig_for_define_next_position in rigs_for_define_next_position:
        if (rig_for_define_next_position.current_position.id,) not in rigs_for_define_next_position_already_in_model:
            NextPosition(current_position=rig_for_define_next_position.current_position).save()


def _get_rigs_for_calculation_rating(start_date_for_calculation: datetime.date,
                                     end_date_for_calculation: datetime.date) -> QuerySet:
    """Получает список буровых установок, которые выйдут из бурения в течении определенного периода"""

    _get_status_to_pads()

    return (RigPosition.objects.filter(end_date__range=(start_date_for_calculation, end_date_for_calculation)) &
            RigPosition.objects.filter(pad__status='drilling').order_by('end_date'))


def _get_status_to_pads() -> None:
    """Присваивает статус 'в бурении/пробурен' кустам"""

    Pad.objects.all().update(status='')

    # Всем кустам, упомянутым в модели RigPosition, присваивается статус "drilling"
    for rig_position in RigPosition.objects.all():
        Pad.objects.filter(id=rig_position.pad.id).update(status='drilling')

        # Если буровая установка упомниается больше одного раза, то всем кустам, на которых была данная БУ (кроме
        # последнего), присваивается статус "drilled"
        rig_position_for_one_DR = RigPosition.objects.filter(drilling_rig=rig_position.drilling_rig)
        if rig_position_for_one_DR.count() > 1:
            for rig_position_ in list(rig_position_for_one_DR)[:-1]:
                Pad.objects.filter(id=rig_position_.pad.id).update(status='drilled')

    for pad in Pad.objects.all():
        if (pad.id,) in list(NextPosition.objects.filter(status='Подтверждено').values_list('next_position')):
            Pad.objects.filter(id=pad.id).update(status='commited_next_positions')
