from dvizhenie.models import Pad, NextPosition, PositionRating, RigPosition, DrillingRig
from django.db.utils import IntegrityError


def handle_uploaded_file(f):
    """Загружает файл на сервер"""

    with open("dvizhenie/uploads/Движение_БУ.xlsx", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def _change_next_position(different_next_position: PositionRating):
    """Меняет автоматически полученную следующую позицию на выбранную"""

    try:
        NextPosition.objects.filter(current_position=different_next_position.current_position).update(
            next_position=different_next_position.next_position)
    except IntegrityError:
        NextPosition.objects.filter(next_position=different_next_position.next_position).update(next_position=None)
        NextPosition.objects.filter(current_position=different_next_position.current_position).update(
            next_position=different_next_position.next_position)
    finally:
        NextPosition.objects.filter(current_position=different_next_position.current_position).update(
            status='Изменено. Требуется подтверждение')


def get_search_result(pads_id, rigs_id) -> list:
    """Получает результат поиска в моделях по списку id"""

    result = []
    result_pads_id = []
    result_rigs_id = []
    for pad_id in pads_id:
        pad = Pad.objects.filter(id=pad_id[0])
        rig_position = RigPosition.objects.filter(pad=pad_id[0])
        res_ = [pad, rig_position]
        result_pads_id.append(res_)
    result.append(result_pads_id)

    for rig_id in rigs_id:
        rig = DrillingRig.objects.filter(id=rig_id[0])
        rig_position = RigPosition.objects.filter(drilling_rig=rig_id[0])
        res_ = [rig, rig_position]
        result_rigs_id.append(res_)
    result.append(result_rigs_id)

    return result
