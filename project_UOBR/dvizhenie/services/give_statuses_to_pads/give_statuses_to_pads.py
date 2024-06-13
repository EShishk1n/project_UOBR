from dvizhenie.services.give_statuses_to_pads.give_status_drilled_to_pads import give_status_drilled_to_pads
from dvizhenie.services.give_statuses_to_pads.give_status_drilling_to_pads import give_status_drilling_to_pads
from dvizhenie.services.give_statuses_to_pads.give_status_free_to_pads import give_status_free_to_pads, \
    update_status_free_to_pads
from dvizhenie.services.give_statuses_to_pads.give_status_reserved_to_pads import give_status_reserved_to_pads


def give_statuses_to_pads() -> None:
    """Присваивает статусы кустам"""

    give_status_drilled_to_pads()
    give_status_drilling_to_pads()
    give_status_reserved_to_pads()
    give_status_free_to_pads()
    update_status_free_to_pads()
