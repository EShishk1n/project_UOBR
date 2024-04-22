from dvizhenie.models import NextPosition
from dvizhenie.services.define_position.define_position import define_position_and_put_into_DB


def define_next_position_after_changes() -> None:

    define_position_and_put_into_DB(
        start_date_for_calculation=NextPosition.objects.exclude(status='commited').first().current_position.end_date,
        end_date_for_calculation=NextPosition.objects.last().current_position.end_date)
