from dvizhenie.models import Pad, DrillingRig, RigPosition


def get_search_result(pads_id: list, rigs_id: list) -> dict:
    """Получает результат поиска в моделях по списку id"""

    result_pads = []
    result_rigs = []
    result_rigs_position = []

    for pad_id in pads_id:
        res = get_search_result_by_model(pad_id, 'Pad')
        result_pads.append(res['model_objs'])
        result_rigs_position.append(res['rig_position_objs'])

    for rig_id in rigs_id:
        res = get_search_result_by_model(rig_id, 'DrillingRig')
        result_rigs.append(res['model_objs'])
        result_rigs_position.append(res['rig_position_objs'])

    return {'result_pads': result_pads, 'result_rigs': result_rigs, 'result_rigs_position': result_rigs_position}


def get_search_result_by_model(model_id: int, model: str) -> dict:

    if model == 'Pad':
        model_objs = Pad.objects.filter(id=model_id)
    else:
        model_objs = DrillingRig.objects.filter(id=model_id)
    rig_position_objs = RigPosition.objects.filter(pad=model_id)

    return {'model_objs': model_objs, 'rig_position_objs': rig_position_objs}
