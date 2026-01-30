from django.db import models


class HornbostelSachs(models.Model):
    instrument = models.ForeignKey(
        "Instrument",
        on_delete=models.CASCADE,
        related_name="hbs_entries",
    )

    hbs_class = models.CharField(
        max_length=50, null=True, help_text="Hornbostel-Sachs classification"
    )

    is_main = models.BooleanField(
        default=False,
        help_text="Is this the main HBS classification for this instrument?",
    )

    review_status = models.CharField(
        max_length=50,
        choices=[
            ("verified", "Verified"),
            ("unverified", "Unverified"),
            ("under_review", "Under Review"),
            ("needs_additional_review", "Needs Additional Review"),
            ("rejected", "Rejected"),
        ],
        default="unverified",
    )

    contributor = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # TODO: add verified_by field to track who verified the name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_main:
            Instrument = self._meta.get_field("instrument").related_model
            instrument = self.instrument
            if instrument.hornbostel_sachs_class_id != self.id:
                instrument.hornbostel_sachs_class = self
                instrument.save(update_fields=["hornbostel_sachs_class"])

            # If there is another HBS object set as main for this instrument, unset others
            other_mains = (
                type(self)
                .objects.filter(instrument=self.instrument, is_main=True)
                .exclude(pk=self.pk)
            )
            if other_mains.exists():
                other_mains.update(is_main=False)
