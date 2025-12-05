from django.db import models


class Source(models.Model):
    name = models.CharField(
        max_length=50, blank=False, help_text="Who or what called the instrument this?"
    )

    is_visible = models.BooleanField(
        default=True, help_text="Should this source be visible?"
    )

    def __str__(self):
        return f"{self.name}"
