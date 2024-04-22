from django.db.models import QuerySet


def update_NextPosition(next_position_queryset: QuerySet, status='',
                        reset_next_position=False, delete_next_position=False) -> None:

    if delete_next_position:
        next_position_queryset.delete()

    else:
        if reset_next_position:
            next_position_queryset.update(next_position=None)

        next_position_queryset.update(status=status)
