"""
Email utilities for user verification and notifications.
Provides async email sending and token generation for email verification.
"""

import threading
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User


def send_email_async(subject, body_html, to_emails):
    """
    Send HTML email asynchronously using threading to avoid blocking the request.

    Args:
        subject: Email subject line
        body_html: HTML content of the email
        to_emails: List of recipient email addresses
    """

    def send_email_task():
        email = EmailMessage(
            subject=subject,
            body=body_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails,
        )
        email.content_subtype = "html"
        email.send()

    # Use daemon thread to prevent blocking shutdown
    thread = threading.Thread(target=send_email_task, daemon=True)
    thread.start()


def generate_verification_token(user):
    """
    Generate a verification token for a user using Django's token generator.

    Args:
        user: User instance

    Returns:
        tuple: (uidb64, token) - URL-safe base64 encoded user ID and token
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


def validate_verification_token(uidb64, token):
    """
    Validate a verification token and return the associated user.

    Args:
        uidb64: URL-safe base64 encoded user ID
        token: Verification token

    Returns:
        User instance if valid, None otherwise
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    # Check if token is valid
    if default_token_generator.check_token(user, token):
        return user
    return None


def send_verification_email(user, request):
    """
    Send verification email to a newly registered user.

    Args:
        user: User instance
        request: HTTP request object (to build absolute URL)
    """
    # Generate verification token
    uidb64, token = generate_verification_token(user)

    # Build verification URL
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()
    verification_url = f"{protocol}://{domain}/verify-email/{uidb64}/{token}/"

    # Render email template
    context = {
        "user": user,
        "verification_url": verification_url,
        "site_name": settings.SITE_NAME,
    }
    body_html = render_to_string("main/registration/verification_email.html", context)

    # Send email asynchronously
    subject = f"Verify your {settings.SITE_NAME} account"
    send_email_async(
        subject=subject,
        body_html=body_html,
        to_emails=[user.username],  # username is the email
    )
