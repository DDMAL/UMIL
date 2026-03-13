"""Shared URL-resolution for instrument images.

Both AVResource (ORM model) and ThumbnailStub (Solr result proxy) need to
turn a relative image path into a full URL.  The rule is the same in both
places:

    uploads/…  →  MEDIA_URL  +  path   (user-uploaded files)
    downloads/…  →  MEDIA_URL  +  path   (downloaded Wikidata images)
    anything else →  STATIC_URL  +  path   (bundled static files)

This module owns that rule once.  Callers that already have an absolute URL
(starts with "/" or "http") or an empty string can skip the call entirely.
"""

from django.conf import settings


def resolve_image_url(path: str) -> str:
    """Return the full URL for a relative image *path*.

    Args:
        path: Relative path as stored in the database or returned by Solr
              (e.g. ``"uploads/instrument_imgs/thumbnail/UMIL-00001.png"``,
              ``"downloads/original/Q12345.jpg"``,
              or ``"instruments/images/…"``).
              An empty string or an already-absolute URL (``/…`` / ``http…``)
              is returned unchanged.
    """
    if not path or path.startswith(("/", "http")):
        return path

    if path.startswith(("uploads/", "downloads/")):
        return f"{settings.MEDIA_URL}{path}"

    return f"{settings.STATIC_URL}{path}"
