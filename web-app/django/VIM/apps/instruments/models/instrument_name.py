from django.db import models


class InstrumentName(models.Model):
    instrument = models.ForeignKey("Instrument", on_delete=models.CASCADE)
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    name = models.CharField(max_length=100, blank=False)

    # An instrument name may be supported by multiple sources, each with its own contributor
    sources = models.ManyToManyField(
        "Source", through="InstrumentNameSource", related_name="instrument_names"
    )
    umil_label = models.BooleanField(
        default=False,
        help_text="Is this the label for the instrument? If true, it will be used as the main name.",
    )

    on_wikidata = models.BooleanField(
        default=False,
        help_text="Is this name already on Wikidata?",
    )

    verification_status = models.CharField(
        max_length=50,
        choices=[
            ("verified", "Verified"),
            ("unverified", "Unverified"),
            ("under_review", "Under Review"),
            ("needs_additional_review", "Needs Additional Review"),
            ("rejected", "Rejected"),
        ],
        default="unverified",
        help_text="Status of the name entry",
    )

    # Custom validation to ensure at most one UMIL label per instrument language
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "language"],
                condition=models.Q(umil_label=True),
                name="unique_umil_label_per_instrument_language",
            )
        ]
