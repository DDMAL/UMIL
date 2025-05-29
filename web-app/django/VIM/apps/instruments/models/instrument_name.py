from django.db import models


class InstrumentName(models.Model):
    instrument = models.ForeignKey("Instrument", on_delete=models.CASCADE)
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    name = models.CharField(max_length=100, blank=False)
    source_name = models.CharField(
        max_length=50, blank=False, help_text="Who or what called the instrument this?"
    )  # Stand-in for source data; format TBD
    status = models.CharField(
        max_length=20,
        choices=[
            ("verified", "Verified"),
            ("unverified", "Unverified"),
            ("uploaded", "Uploaded"),
        ],
        default="unverified",
        help_text="Status of the name entry",
    )
    is_alias = models.BooleanField(
        default=False,
        help_text="Is this an alias for the instrument? If true, it will not be used as the main name.",
    )
    contributor = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who contributed this name",
    )