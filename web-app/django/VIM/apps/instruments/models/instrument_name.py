from django.db import models


class InstrumentName(models.Model):
    instrument = models.ForeignKey("Instrument", on_delete=models.PROTECT)
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    name = models.CharField(max_length=50, blank=False)
    source_name = models.CharField(
        max_length=50, blank=False, help_text="Who or what called the instrument this?"
    )
    source_type = models.CharField(
        max_length=50, blank=False, help_text="What type of source is this?"
    )
    source_date = models.DateField(blank=False, help_text="Date of source")
    # source_location
    source_description = models.TextField(
        blank=True, help_text="Additional information about the source of this name."
    )
    description_language = models.ForeignKey(
        "Language",
        on_delete=models.PROTECT,
        blank=True,
        null = True,
        help_text="What language is Source Description written in?",
        related_name = "instrument_name_description_language",
    )
