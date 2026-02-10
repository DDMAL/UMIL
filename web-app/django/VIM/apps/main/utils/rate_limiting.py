"""Rate limiting utilities for email operations."""

import hashlib
import time
from django.conf import settings
from django.core.cache import cache


def get_email_cooldown_remaining(email):
    """
    Return remaining cooldown seconds for an email (0 if none).

    Args:
        email: Email address to check

    Returns:
        int: Remaining seconds (0 if no cooldown active)
    """
    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
    cache_key = f"email_resend_cooldown:{email_hash}"
    expiration_time = cache.get(cache_key)

    if expiration_time:
        remaining = int(expiration_time - time.time())
        return max(0, remaining)
    return 0


def check_email_resend_cooldown(email):
    """
    Check if email resend is allowed and return remaining cooldown time.

    Uses atomic cache.add() (set-if-not-exists) to prevent TOCTOU races.

    Args:
        email: Email address to check cooldown for

    Returns:
        tuple: (allowed: bool, remaining_seconds: int)
    """
    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
    cache_key = f"email_resend_cooldown:{email_hash}"
    current_time = time.time()
    expiration_time = current_time + settings.RESEND_EMAIL_COOLDOWN

    # Atomically start cooldown only if not already set.
    added = cache.add(
        cache_key, expiration_time, timeout=settings.RESEND_EMAIL_COOLDOWN
    )

    if added:
        return True, 0

    # Cooldown already active; compute remaining time.
    existing_expiration = cache.get(cache_key)
    if existing_expiration:
        remaining = int(existing_expiration - current_time)
        if remaining > 0:
            return False, remaining
        # Cooldown expired but key still present (backend quirk).
        # Set new cooldown to prevent race condition with concurrent requests.
        cache.set(cache_key, expiration_time, timeout=settings.RESEND_EMAIL_COOLDOWN)
        return True, 0

    # Key disappeared between add() and get().
    # Set new cooldown to prevent race condition with concurrent requests.
    cache.set(cache_key, expiration_time, timeout=settings.RESEND_EMAIL_COOLDOWN)
    return True, 0
