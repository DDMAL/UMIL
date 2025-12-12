"""Rate limiting utilities for email operations."""

import hashlib
import time
from django.conf import settings
from django.core.cache import cache


def get_email_cooldown_remaining(email):
    """
    Get remaining cooldown time for an email without setting cooldown.

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

    Args:
        email: Email address to check cooldown for

    Returns:
        tuple: (allowed: bool, remaining_seconds: int)
    """
    remaining = get_email_cooldown_remaining(email)

    if remaining > 0:
        return False, remaining

    # Set cooldown by storing expiration timestamp
    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
    cache_key = f"email_resend_cooldown:{email_hash}"
    expiration_time = time.time() + settings.RESEND_EMAIL_COOLDOWN
    cache.set(cache_key, expiration_time, timeout=settings.RESEND_EMAIL_COOLDOWN)
    return True, 0
