from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class type_of_DR(models.Model):
    """Типовые буровые установки"""

    type = models.CharField(unique=True)

    def __str__(self):
        return f'{self.type}'


class Contractor(models.Model):
    """Типовые наименования подрядных организаций по бурению"""

    contractor = models.CharField()

    def __str__(self):
        return f'{self.contractor}'


class Mud(models.TextChoices):
    """Типы применяемых буровых растворов"""

    ruo = 'РУО', 'РУО'
    rvo = 'РВО', 'РВО'


class Field(models.TextChoices):
    """Основные месторождения на проекте РН-ЮНГ"""

    VS = 'ВС', 'Восточно-Сургутское'
    VTK = 'ВТК', 'Восточно-Токайское'
    VPR = 'ВПР', 'Восточно-Правдинское'
    VSTR = 'ВСТР', 'Встречное'
    EFR = 'ЕФР', 'Ефремовское'
    ZUG = 'ЗУГ', 'Западно-Угутское'
    KIN = 'КИН', 'Киняминское'
    KUZ = 'КУЗ', 'Кузоваткинское'
    KUDR = 'КУДР', 'Кудринское'
    MB = 'МБ', 'Малобалыкское'
    MAM = 'МАМ', 'Мамонтовское'
    MAY = 'МАЙ', 'Майское'
    MOSK = 'МОСК', 'Московцева'
    OMB = 'ОМБ', 'Омбинское'
    PET = 'ПЕТ', 'Петелинское'
    PRD = 'ПРД', 'Правдинское'
    PROp = 'ПРОп', 'Приобское (правый)'
    PROl = 'ПРОл', 'Приобское (левый)'
    ERG = 'ЭРГ', 'Эргинское'
    PRZ = 'ПРЗ', 'Приразломное'
    SAL = 'САЛ', 'Салымское'
    SOL = 'СОЛ', 'Солкинское'
    SOR = 'СОР', 'Соровское'
    SB = 'СБ', 'Среднебалыкское'
    SUG = 'СУГ', 'Среднеугутское'
    UG = 'УГ', 'Угутское'
    UB = 'УБ', 'Усть-Балыкское'
    FN = 'ФН', 'Фаинское'
    YB = 'ЮБ', 'Южно-Балыкское'
    YTEPL = 'ЮТЕПЛ', 'Южно-Тепловское'
    YS = 'ЮС', 'Южно-Сургутское'


class DrillingRig(models.Model):
    """Буровые установки с основной информацией"""

    objects = models.Manager()
    type = models.ForeignKey(type_of_DR, on_delete=models.CASCADE)
    number = models.CharField(unique=True)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    mud = models.CharField(choices=Mud.choices)

    def capacity(self) -> int:
        is_DR_russian = str(self.type)[4]
        if is_DR_russian in ['/', '-']:
            return int(str(self.type)[5:])
        else:
            if str(self.type) in ['ZJ-50 2эш', 'ZJ-50 0.5эш', 'Bentec', 'ZJ-50 1эш']:
                return 320
            elif str(self.type) == 'Drillmec':
                return 225

    class Meta:
        ordering = ['contractor', 'type']

    def __str__(self):
        return str(f'БУ {self.type} зав.№{self.number} {self.contractor}')


class Pad(models.Model):
    """Кустовые площадки с основной информацией"""

    objects = models.Manager()

    class Capacity(models.IntegerChoices):
        very_heavy = 400, '400'
        heavy = 320, '320'
        less_than_heavy = 270, '270'
        middle = 250, '250'
        less_than_middle = 225, '225'
        light = 200, '200'
        new = 0, '0'

    number = models.CharField()
    field = models.CharField(choices=Field.choices, null=False, blank=True)
    first_stage_date = models.DateField(null=False, blank=True)
    second_stage_date = models.DateField(null=False, blank=True)
    required_capacity = models.IntegerField(choices=Capacity.choices)
    required_mud = models.CharField(choices=Mud.choices, null=False, blank=True)
    gs_quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(24)])
    nns_quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(24)])

    class marker(models.TextChoices):
        ordinary = 'нет', 'обычный куст'
        special_project = 'для 2эш', 'для 2эш'
        SNPH = 'СНПХ', 'возможно бурение СНПХ'
        priority = 'приоритет', 'приоритетное движение'

    marker = models.CharField(choices=marker.choices, default=marker.ordinary)
    status = models.CharField(default='')

    class Meta:
        ordering = ['first_stage_date']

    def __str__(self):
        return str(f'{self.number} {self.field}')


class RigPosition(models.Model):
    """Текущее местоположение буровых установок"""

    objects = models.Manager()
    drilling_rig = models.ForeignKey(DrillingRig, on_delete=models.CASCADE)
    pad = models.ForeignKey(Pad, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['end_date']

    def __str__(self):
        return str(f'{self.pad}')


class NextPosition(models.Model):
    """Пары буровая-следущий куст"""

    objects = models.Manager()
    current_position = models.OneToOneField(RigPosition, on_delete=models.CASCADE)
    next_position = models.OneToOneField(Pad, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(default='')

    def __str__(self):
        return str(f'Буровой установке {self.current_position} определено движение на {self.next_position}')


class PositionRating(models.Model):
    """Пары буровая-следующий куст с рейтингами"""

    objects = models.Manager()
    current_position = models.ForeignKey(RigPosition, on_delete=models.CASCADE)
    next_position = models.ForeignKey(Pad, on_delete=models.CASCADE)
    capacity_rating = models.FloatField()
    first_stage_date_rating = models.FloatField()
    second_stage_date_rating = models.FloatField()
    mud_rating = models.FloatField()
    logistic_rating = models.FloatField()
    marker_rating = models.FloatField()
    strategy_rating = models.FloatField()
    common_rating = models.FloatField()
    status = models.CharField(default='')

    class Meta:
        ordering = ["current_position"]

    def __str__(self):
        return str(f'{self.current_position} {self.next_position} {self.common_rating}')
