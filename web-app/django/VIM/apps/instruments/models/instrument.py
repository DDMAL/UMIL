from django.db import models


class Instrument(models.Model):
    wikidata_id = models.CharField(max_length=20, unique=True)
    default_image = models.ForeignKey(
        "AVResource",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="default_image_of",
    )
    thumbnail = models.ForeignKey(
        "AVResource",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="thumbnail_of",
    )
    hornbostel_sachs_class = models.CharField(
        max_length=50, blank=True, help_text="Hornbostel-Sachs classification"
    )
    mimo_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="Musical Instrument Museums Online classification",
    )
