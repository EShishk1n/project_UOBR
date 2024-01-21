from django import forms


from dvizhenie.models import DrillingRig


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