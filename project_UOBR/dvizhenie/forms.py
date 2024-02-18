from django import forms
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from dvizhenie.models import DrillingRig, Pad, RigPosition


class DrillingRigForm(forms.ModelForm):
    class Meta:
        model = DrillingRig
        fields = '__all__'
        labels = {
            'type': 'Тип буровой установки',
            'number': 'Заводской номер',
            'contractor': 'Буровой подрядчик',
            'mud': 'Тип бурового раствора',
        }


class PadForm(forms.ModelForm):
    class Meta:
        model = Pad
        fields = (
            'number', 'field', 'first_stage_date', 'second_stage_date', 'required_capacity', 'required_mud',
            'gs_quantity',
            'nns_quantity', 'marker')
        labels = {
            'number': 'Кустовая площадка №',
            'field': 'Месторождение',
            'first_stage_date': 'Готовность 1 этапа отсыпки',
            'second_stage_date': 'Готовность 2 этапа отсыпки',
            'required_capacity': 'Требуемая грузоподъемность',
            'required_mud': 'Требуемый тип бурового раствора',
            'gs_quantity': 'Количество горизонтальных скважин',
            'nns_quantity': 'Количество наклонно-направленных скважин',
            'marker': 'Маркер',
        }


class RigPositionAddForm(forms.ModelForm):
    class Meta:
        model = RigPosition
        fields = (
            'drilling_rig', 'pad', 'end_date')
        labels = {
            'drilling_rig': 'БУ с мобилизации',
            'pad': 'откуда',
            'end_date': 'Готовность к транспортировке на КП',
        }


class RigPositionForm(forms.ModelForm):
    class Meta:
        model = RigPosition
        fields = ('start_date', 'end_date')
        labels = {
            'start_date': 'Начало бурения',
            'end_date': 'Окончание бурения',
        }


class UploadFileForm(forms.Form):
    file = forms.FileField(label='')


class ExportDataForm(forms.Form):
    table_start_row = forms.IntegerField(label='Первая строка экспортируемого интервала')
    table_end_row = forms.IntegerField(label='Последняя строка экспортируемого интервала')


class DefinePositionForm(forms.Form):
    start_date_for_calculation = forms.DateField(label='начало периода для расчета')
    end_date_for_calculation = forms.DateField(label='окончание периода для расчета')
