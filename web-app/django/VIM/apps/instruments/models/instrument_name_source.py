from django.db import models


class InstrumentNameSource(models.Model):
    instrument_name = models.ForeignKey(
        "InstrumentName", on_delete=models.CASCADE, related_name="source_links"
    )
    source = models.ForeignKey("Source", on_delete=models.CASCADE)

    contributor = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        help_text="Users who contributed this source to this name",
        related_name="instrument_name_sources",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.source.name} for {self.instrument_name.name}"
