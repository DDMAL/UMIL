from django.db import models
from django.db.models import Q


class InstrumentName(models.Model):
    instrument = models.ForeignKey("Instrument", on_delete=models.CASCADE)
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    name = models.CharField(max_length=100, blank=False)
    source_name = models.CharField(
        max_length=50, blank=False, help_text="Who or what called the instrument this?"
    )  # Stand-in for source data; format TBD
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
    umil_label = models.BooleanField(
        default=False,
        help_text="Is this the label for the instrument? If true, it will be used as the main name.",
    )
    contributor = models.ForeignKey(
        "auth.User",
        null=False,
        on_delete=models.PROTECT,
        help_text="User who contributed this name",
    )
    on_wikidata = models.BooleanField(
        default=False,
        help_text="Is this name already on Wikidata?",
    )
    deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag. If true, this name is considered deleted but retained in the database.",
    )

    # Constrain umil_label to be true only if the name is verified and not deleted
    class Meta:
        constraints = [
            models.CheckConstraint(
                name="umil_label=true only if name is Verified and not Deleted",
                check=~Q(umil_label=True)
                | (Q(verification_status="verified") & Q(deleted=False)),
            ),
        ]

    # TODO: add verified_by field to track who verified the name
    def __str__(self):
        return f"{self.name} ({self.language.en_label}) - {self.instrument.wikidata_id}"

    def save(self, *args, **kwargs):
        # Querysets for efficiency
        existing_umil_label_qs = InstrumentName.objects.filter(
            instrument=self.instrument,
            language=self.language,
            umil_label=True,
        ).exclude(id=self.id)

        replacement_umil_label_qs = InstrumentName.objects.filter(
            instrument=self.instrument,
            language=self.language,
            verification_status="verified",
            deleted=False,
        ).exclude(id=self.id)

        # If setting umil_label=True
        if self.umil_label:
            if self.deleted:
                # Assign replacement if possible, else just unset
                self.umil_label = False
                super().save(*args, **kwargs)

                replacement_umil_label_qs.update(umil_label=True)
                return
            else:
                # Unset other umil_labels in one query
                existing_umil_label_qs.update(umil_label=False)

        # If a verified name is removing itself as umil_label
        if not self.umil_label and self.verification_status == "verified":
            # Try to assign replacement label in one query
            replaced = replacement_umil_label_qs.update(umil_label=True)
            if not replaced:
                # If there is no replacement umil_label, only set umil_label=False if the current name is also deleted
                # Otherwise, a viewer will see a verified name on the detail page without a label
                if self.deleted:
                    self.umil_label = False
                else:
                    raise ValueError(
                        "This is the only verified, non-deleted name for this instrument and language, it must be set as umil_label."
                    )

        super().save(*args, **kwargs)
