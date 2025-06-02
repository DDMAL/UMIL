from django import forms
from ..models.instrument_name import InstrumentName

class NameForm(forms.ModelForm):
    class Meta:
        model = InstrumentName
        fields =  ['instrument', 'language', 'name', 'source_name', 'is_alias']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
        help_texts = {
            'source_name': '',
            'is_alias': '',
        }