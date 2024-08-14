from django.db import models


class AVResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ("audio", "Audio"),
        ("video", "Video"),
        ("image", "Image"),
    ]

    instrument = models.ForeignKey("Instrument", on_delete=models.SET_NULL, null=True)
    type = models.CharField(
        max_length=5,
        choices=RESOURCE_TYPE_CHOICES,
        blank=False,
        help_text="What type of audiovisual resource is this?",
    )
    format = models.CharField(
        blank=False
    )  # This should eventually be a choice field with supported formats
    url = models.URLField(blank=False, max_length=1000)
    instrument_date = models.DateField(
        blank=True, null=True, help_text="When was this instrument made?"
    )
    instrument_maker = models.CharField(
        blank=True, help_text="Who made this instrument?"
    )
    # instrument_location; TBD how to manage location data
    instrument_description = models.TextField(
        blank=True, help_text="Additional information about the instrument."
    )
    instrument_description_language = models.ForeignKey(
        "Language",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="What language is Instrument Description written in?",
    )
    source_name = models.CharField(
        blank=False, help_text="What is the name of the source of this AVResource?"
    )  # Stand-in for source data; format TBD
