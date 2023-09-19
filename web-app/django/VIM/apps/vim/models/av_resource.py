from django.db import models


class AVResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ("audio", "Audio"),
        ("video", "Video"),
        ("image", "Image"),
    ]

    instrument = models.ForeignKey("Instrument", on_delete=models.PROTECT)
    type = models.CharField(
        max_length=5,
        choices=RESOURCE_TYPE_CHOICES,
        blank=False,
        help_text="What type of resource is this?",
    )
    format = models.CharField(
        max_length=50, blank=False
    )  # This should be a choice field with supported formats
    uri = models.URLField(max_length=250, blank=False)
    instrument_date = models.DateField(
        blank=True, help_text="When was this instrument made?"
    )
    instrument_maker = models.CharField(
        max_length=50, blank=True, help_text="Who made this instrument?"
    )
    # instrument_location
    instrument_description = models.TextField(
        blank=True, help_text="Additional information about the instrument."
    )
    instrument_description_language = models.ForeignKey(
        "Language",
        on_delete=models.PROTECT,
        blank=True,
        help_text="What language is Instrument Description written in?",
    )
