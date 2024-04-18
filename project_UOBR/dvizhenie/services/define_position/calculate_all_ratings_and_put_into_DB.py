from datetime import datetime

from django.db.models import QuerySet

from dvizhenie.models import RigPosition, Pad, PositionRating
from dvizhenie.services.define_position.get_rating import get_rating_and_put_into_DB
from dvizhenie.services.give_statuses_to_pads.give_statuses_to_pads import give_statuses_to_pads


def calculate_all_ratings_and_put_into_DB(start_date_for_calculation: datetime.date,
                                          end_date_for_calculation: datetime.date) -> None:
    """Получает рейтинг для каждой пары буровая установка-куст"""

    rigs_for_define_next_position = get_rigs_for_calculation_rating(start_date_for_calculation,
                                                                    end_date_for_calculation)
    free_pads = get_free_pads()
    calculate_ratings_for_positions_and_put_into_DB(rigs_for_define_next_position, free_pads)


def get_rigs_for_calculation_rating(start_date_for_calculation: datetime.date,
                                    end_date_for_calculation: datetime.date) -> QuerySet(RigPosition):
    """Получает список буровых установок, которые выйдут из бурения в течение определенного периода"""

    give_statuses_to_pads()

    return (RigPosition.objects.filter(end_date__range=(start_date_for_calculation, end_date_for_calculation)) &
            RigPosition.objects.filter(pad__status='drilling').order_by('end_date'))


def calculate_ratings_for_positions_and_put_into_DB(rigs: QuerySet(RigPosition), pads: QuerySet(Pad)) -> None:

    clear_PositionRating()

    for rig in rigs:
        for pad in pads:
            get_rating_and_put_into_DB(rig, pad)


def get_free_pads():
    return Pad.objects.exclude(status__in=['drilled', 'drilling', 'reserved'])


def clear_PositionRating() -> None:
    PositionRating.objects.all().delete()
