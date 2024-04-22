from dvizhenie.models import PositionRating, Pad, NextPosition, RigPosition
from dvizhenie.services.give_statuses_to_pads.common_function import give_status_to_pads


def _change_next_position(different_next_position: PositionRating):
    """Меняет автоматически полученную следующую позицию на выбранную"""

    current_position = different_next_position.current_position
    new_next_position = different_next_position.next_position

    give_status_free_to_pad_in_previous_NextPosition(current_position)

    delete_next_position_if_alredy_in_model(new_next_position)

    put_new_next_position_in_NextPosition(current_position, new_next_position)


def give_status_free_to_pad_in_previous_NextPosition(current_position: RigPosition) -> None:

    previos_next_position = [
        NextPosition.objects.filter(current_position=current_position).values_list('next_position')]
    give_status_to_pads(previos_next_position, 'free')


def delete_next_position_if_alredy_in_model(new_next_position: Pad) -> None:
    if (new_next_position.id,) in list(NextPosition.objects.all().values_list('next_position')):
        NextPosition.objects.filter(next_position=new_next_position).update(next_position=None)


def put_new_next_position_in_NextPosition(current_position: RigPosition, new_next_position: Pad) -> None:
    NextPosition.objects.filter(current_position=current_position).update(next_position=new_next_position,
                                                                          status='changed')
