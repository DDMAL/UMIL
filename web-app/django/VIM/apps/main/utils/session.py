"""Session utilities for user verification workflow."""

from django.utils import timezone
from django.conf import settings


def set_pending_verification_email(request, email):
    """Store email in session with timestamp for expiry tracking."""
    request.session["pending_verification_email"] = email
    request.session["pending_verification_timestamp"] = timezone.now().timestamp()


def clear_pending_verification_email(request):
    """Clear pending verification email and timestamp from session."""
    request.session.pop("pending_verification_email", None)
    request.session.pop("pending_verification_timestamp", None)


def get_pending_verification_email(request):
    """
    Get pending verification email if not expired.

    Returns:
        str or None: Email address if valid and not expired, None otherwise
    """
    email = request.session.get("pending_verification_email")
    timestamp = request.session.get("pending_verification_timestamp", 0)

    # Check if email exists and is not expired
    if (
        not email
        or timezone.now().timestamp() - timestamp
        > settings.PENDING_EMAIL_SESSION_EXPIRY
    ):
        return None

    return email
