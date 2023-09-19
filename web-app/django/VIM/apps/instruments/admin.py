from django.contrib import admin
from VIM.apps.instruments.models import Instrument, InstrumentName, Language, AVResource

admin.site.register(Instrument)
admin.site.register(InstrumentName)
admin.site.register(Language)
admin.site.register(AVResource)
