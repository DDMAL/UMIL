import os
from django.core.exceptions import ValidationError
from django.db import models
from VIM.apps.instruments.constants import IMAGE_FORMAT_CHOICES


def avresource_upload_path(instance, filename):
    """
    Generate upload path for AVResource files.
    Format: uploads/instrument_imgs/{original|thumbnail}/{umil_id}.{ext}

    Uses instance.is_thumbnail flag to determine subdirectory.

    Examples:
        - Original: uploads/instrument_imgs/original/UMIL-00001.jpg
        - Thumbnail: uploads/instrument_imgs/thumbnail/UMIL-00001.jpg
    """
    # Get file extension from original filename
    ext = os.path.splitext(filename)[1].lower()

    # Get UMIL ID from instrument
    if instance.instrument and instance.instrument.umil_id:
        umil_id = instance.instrument.umil_id
    else:
        raise ValidationError(
            "Cannot generate upload path: instrument or umil_id is not set on this AVResource."
        )

    # Determine subdirectory based on is_thumbnail flag
    subdir = "thumbnail" if getattr(instance, "is_thumbnail", False) else "original"

    filename = f"{umil_id}{ext}"
    return os.path.join("uploads", "instrument_imgs", subdir, filename)


class AVResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ("audio", "Audio"),
        ("video", "Video"),
        ("image", "Image"),
    ]

    def __init__(self, *args, **kwargs):
        """
        Initialize AVResource with optional is_thumbnail flag.

        The is_thumbnail flag is used by avresource_upload_path() to determine
        whether to save to the 'original' or 'thumbnail' subdirectory.
        """
        self.is_thumbnail = kwargs.pop("is_thumbnail", False)
        super().__init__(*args, **kwargs)

    instrument = models.ForeignKey("Instrument", on_delete=models.SET_NULL, null=True)
    type = models.CharField(
        max_length=5,
        choices=RESOURCE_TYPE_CHOICES,
        blank=False,
        help_text="What type of audiovisual resource is this?",
    )
    format = models.CharField(
        max_length=10,
        choices=IMAGE_FORMAT_CHOICES,
        blank=False,
        help_text="Image file format extension",
    )
    url = models.CharField(blank=True, max_length=1000)
    file = models.ImageField(
        upload_to=avresource_upload_path,
        blank=True,
        null=True,
        help_text="Uploaded image file",
    )
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
        max_length=200,
        blank=False,
        help_text="What is the name of the source of this AVResource?",
    )  # Stand-in for source data; format TBD
    created_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_avresources",
        help_text="User who uploaded this resource (null for imports)",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "url"],
                condition=models.Q(url__gt=""),
                name="unique_instrument_url",
            )
        ]

    def clean(self):
        super().clean()
        if not self.url and not self.file:
            raise ValidationError("Either URL or file must be provided")

    def get_image_url(self):
        """Return the URL for accessing the image."""
        from VIM.apps.instruments.utils.image_urls import resolve_image_url

        # file.name is the relative path stored in the DB (e.g. uploads/…);
        # resolve_image_url applies the same MEDIA_URL / STATIC_URL rule used
        # by ThumbnailStub so the two stay in sync.
        if self.file:
            return resolve_image_url(self.file.name)

        if self.url:
            return resolve_image_url(self.url)

        return ""
