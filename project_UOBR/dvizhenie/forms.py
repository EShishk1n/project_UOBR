from django import forms

from dvizhenie.models import DrillingRig


class DrillingRigRorm(forms.ModelForm):
    class Meta:
        model = DrillingRig
        fields = '__all__'

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number'].widget.attrs.update({'class': 'form-control'})
