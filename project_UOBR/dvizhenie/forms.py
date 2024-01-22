from django import forms


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
        fields = '__all__'
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


class RigPositionForm(forms.ModelForm):
    class Meta:
        model = RigPosition
        fields = ('end_date',)
        labels = {
            'end_date': '',
        }
