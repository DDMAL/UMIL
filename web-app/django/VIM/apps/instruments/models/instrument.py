from django.db import models


class Instrument(models.Model):
    umil_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="UMIL unique identifier (e.g., UMIL-00001)",
    )
    wikidata_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text="Wikidata Q-number (e.g., Q5994). Null for user-created instruments.",
    )
    default_image = models.ForeignKey(
        "AVResource",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="default_image_of",
    )
    thumbnail = models.ForeignKey(
        "AVResource",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="thumbnail_of",
    )
    hornbostel_sachs_class = models.ForeignKey(
        "HornbostelSachs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_for",
        help_text="Currently selected Hornbostel–Sachs classification",
    )
    mimo_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="Musical Instrument Museums Online classification",
    )
    created_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_instruments",
        help_text="User who created this instrument (null for Wikidata imports)",
    )
    source = models.CharField(
        max_length=200,
        blank=True,
        help_text="Source/reference for this instrument entry",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        help_text="When this instrument was created",
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
        help_text="Verification status of the instrument",
    )
    needs_reindexing = models.BooleanField(
        default=False,
        help_text="True if Solr indexing failed and needs retry",
    )

    @classmethod
    def generate_umil_id(cls) -> str:
        """
        Generate next available UMIL identifier for all instruments.
        Uses row-level locking to prevent race conditions during concurrent creation.

        IMPORTANT: This method MUST be called within a transaction.atomic() block
        to ensure the select_for_update() lock is held until the new instrument is saved.
        """
        # Lock the last UMIL instrument row to prevent concurrent access
        # The lock will be held until the enclosing transaction commits
        last_instrument = (
            cls.objects.select_for_update()
            .filter(umil_id__startswith="UMIL-")
            .order_by("-umil_id")
            .first()
        )

        if last_instrument:
            last_num = int(last_instrument.umil_id.split("-")[1])
            return f"UMIL-{last_num + 1:05d}"
        return "UMIL-00001"

    @property
    def is_user_created(self) -> bool:
        """Check if this instrument was created by a user (not from Wikidata)."""
        return self.wikidata_id is None or self.wikidata_id == ""

    def __str__(self):
        return f"{self.umil_id}"
