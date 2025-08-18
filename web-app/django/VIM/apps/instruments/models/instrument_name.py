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

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="umil_label_only_if_verified_and_not_deleted",
                check=~Q(umil_label=True)
                | (Q(verification_status="verified") & Q(deleted=False)),
            ),
        ]

    # TODO: add verified_by field to track who verified the name
    def __str__(self):
        return f"{self.name} ({self.language.en_label}) - {self.instrument.wikidata_id}"

    def save(self, *args, **kwargs):
        """
        umil_label
        """
        existing_umil_label = InstrumentName.objects.filter(
            instrument=self.instrument,
            language=self.language,
            umil_label=True,
        ).exclude(id=self.id)
        print("existing_umil_label", existing_umil_label.exists(), flush=True)

        replacement_umil_label = (
            InstrumentName.objects.filter(
                instrument=self.instrument,
                language=self.language,
                verification_status="verified",
                deleted=False,
            )
            .exclude(id=self.id)
            .first()
        )
        print("replacement_umil_label", replacement_umil_label, flush=True)

        if self.umil_label:
            if self.deleted:
                if replacement_umil_label:
                    self.umil_label = False
                    replacement_umil_label.umil_label = True
                    replacement_umil_label.save()
                else:
                    self.umil_label = False
                    return super().save(*args, **kwargs)
            else:
                if existing_umil_label.exists():
                    existing_umil_label.update(umil_label=False)
                else:
                    return super().save(*args, **kwargs)

        if not self.umil_label and self.verification_status == "verified":
            if replacement_umil_label:
                replacement_umil_label.umil_label = True
                replacement_umil_label.save()
            else:
                if self.deleted:
                    self.umil_label = False
                else:
                    self.umil_label = True

        super().save(*args, **kwargs)
