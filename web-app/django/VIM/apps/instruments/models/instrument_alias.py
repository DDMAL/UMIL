from django.db import models


class InstrumentAlias(models.Model):
    instrument_name = models.ForeignKey("InstrumentName", on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, blank=False)
    source_name = models.CharField(
        max_length=50, blank=False, help_text="Who or what called the instrument this?"
    )  # Stand-in for source data; format TBD
    is_verified = models.BooleanField(default=False)