from django import forms
from ..models.instrument_name import InstrumentName

class NameForm(forms.ModelForm):
    class Meta:
        model = InstrumentName
        fields =  ['language', 'name', 'source_name']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
        help_texts = {
            'source_name': ''
        }