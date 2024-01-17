from django.db import models


def get_info_from_BD(model_name: models) -> list:
    """Получает все данные из выбранной таблицы"""

    return model_name.objects.all()


def delete_info_from_BD(model_name: models, id: int) -> None:
    """Удаляет данные из выбранной таблицы по переданному id"""

    model_name.objects.filter(id=id).delete()
