from django.db import models


class InstrumentName(models.Model):
    instrument = models.ForeignKey("Instrument", on_delete=models.PROTECT)
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    name = models.CharField(max_length=50, blank=False)
    source_name = models.CharField(
        max_length=50, blank=False, help_text="Who or what called the instrument this?"
    )  # Stand-in for source data; format TBD
