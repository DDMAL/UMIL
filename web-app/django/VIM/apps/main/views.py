import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from VIM.apps.instruments.models import Instrument, Language, InstrumentName
from VIM.apps.main.forms import (
    EmailUserCreationForm,
    EmailAuthenticationForm,
)
from VIM.apps.main.utils.email import (
    send_verification_email,
    validate_verification_token,
)
from VIM.apps.main.utils.rate_limiting import (
    check_email_resend_cooldown,
    get_email_cooldown_remaining,
)
from VIM.apps.main.utils.session import (
    set_pending_verification_email,
    clear_pending_verification_email,
    get_pending_verification_email,
)


def home(request):
    # Fetch statistics from database
    total_instruments = Instrument.objects.count()
    total_languages = Language.objects.count()
    total_names = InstrumentName.objects.count()
    total_editors = User.objects.count()

    # Chart data: Top 5 instruments with most languages
    top_instruments_by_languages = (
        Instrument.objects.annotate(
            language_count=Count("instrumentname__language", distinct=True)
        )
        .filter(language_count__gt=0)  # Only instruments with at least one language
        .order_by("-language_count")[:5]
    )

    instruments_chart_data = []
    for instrument in top_instruments_by_languages:
        # Get the English name if available, otherwise use the first available name
        try:
            english_name = instrument.instrumentname_set.filter(
                language__en_label="English"
            ).first()
            name = (
                english_name.name
                if english_name
                else instrument.instrumentname_set.first().name
            )
        except:
            name = f"Instrument {instrument.wikidata_id}"

        instruments_chart_data.append(
            {"name": name, "count": instrument.language_count}
        )

    # Chart data: Top 5 languages with most instrument names
    top_languages_by_names = (
        Language.objects.annotate(
            instrument_count=Count("instrumentname", distinct=True)
        )
        .filter(
            instrument_count__gt=0
        )  # Only languages with at least one instrument name
        .order_by("-instrument_count")[:5]
    )

    languages_chart_data = []
    for language in top_languages_by_names:
        languages_chart_data.append(
            {"name": language.en_label, "count": language.instrument_count}
        )

    context = {
        "active_tab": "home",
        "total_instruments": total_instruments,
        "total_languages": total_languages,
        "total_names": total_names,
        "total_editors": total_editors,
        "instruments_chart_data": json.dumps(instruments_chart_data),
        "languages_chart_data": json.dumps(languages_chart_data),
    }
    return render(request, "main/index.html", context)


def about(request):
    return render(request, "main/about.html", {"active_tab": "about"})


def custom_login(request):
    """
    Custom login view that handles unverified accounts.
    """
    # Redirect authenticated users to home (or next URL if valid)
    if request.user.is_authenticated:
        next_url = request.GET.get("next", None)
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("main:home")

    if request.method == "POST":
        email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Check if user exists and verify their account status before form validation
        if email and password:
            try:
                user = User.objects.get(username=email)
                # Check if credentials are correct but account is not active
                if not user.is_active and user.check_password(password):
                    # Credentials are correct but account not verified
                    set_pending_verification_email(request, email)
                    messages.warning(
                        request,
                        "Your email isn't verified yet. Please check your inbox for a verification link.",
                    )
                    return redirect("main:verify_email_pending")
            except User.DoesNotExist:
                # User doesn't exist, let form validation handle it
                pass

        # Proceed with normal form validation
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Validate next parameter to prevent open redirect attacks
            next_url = request.GET.get("next", None)
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("main:home")
    else:
        form = EmailAuthenticationForm()

    return render(request, "main/auth/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        # Extract email before form validation to check for existing unverified users
        email = request.POST.get("username", "").strip()

        # Check if unverified user already exists before form validation
        # This must happen before form.is_valid() because UserCreationForm
        # validates username uniqueness during is_valid(), making this check
        # unreachable if placed after form validation
        if email:
            try:
                existing_user = User.objects.get(username=email)
                if not existing_user.is_active:
                    # Unverified account exists - store email and redirect to pending page
                    set_pending_verification_email(request, email)
                    messages.warning(
                        request,
                        "This account already exists but is not verified. Please check your inbox for a verification link.",
                    )
                    return redirect("main:verify_email_pending")
                # Active user exists - let form validation handle it with proper error message
            except User.DoesNotExist:
                # User doesn't exist, proceed with normal registration
                pass

        # Proceed with normal form validation
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            # Create user but not activate it yet
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Check rate limit and send verification email
            allowed, remaining = check_email_resend_cooldown(user.username)
            if allowed:
                send_verification_email(user, request)

            # Store email in session and redirect to pending page
            set_pending_verification_email(request, user.username)
            return redirect("main:verify_email_pending")
    else:
        form = EmailUserCreationForm()

    return render(request, "main/auth/register.html", {"form": form})


def verify_email_pending(request):
    """
    Show email verification pending page with session expiry check.
    """
    email = get_pending_verification_email(request)
    if not email:
        clear_pending_verification_email(request)
        messages.error(
            request, "Session expired. Please login again to request another email."
        )
        return redirect("main:login")

    # Get remaining cooldown for countdown sync
    cooldown_remaining = get_email_cooldown_remaining(email)

    return render(
        request,
        "main/auth/verify_email_pending.html",
        {
            "email": email,
            "cooldown_remaining": cooldown_remaining,
            "cooldown_duration": settings.RESEND_EMAIL_COOLDOWN,
        },
    )


def verify_email(request, uidb64, token):
    """
    Handle email verification when user clicks the link in their email.
    """
    # Validate the token and get the user
    user = validate_verification_token(uidb64, token)

    if user is None:
        messages.error(request, "Invalid or expired verification link.")
    elif user.is_active:
        messages.info(request, "Your account is already verified.")
    else:
        user.is_active = True
        user.save()
        clear_pending_verification_email(request)
        messages.success(request, "Email verified successfully! You can log in now.")

    return redirect("main:login")


def resend_verification_email(request):
    """
    Resend verification email with rate limiting (60s).
    """
    if request.method != "POST":
        return redirect("main:login")

    email = request.POST.get("email", "").strip()

    # Validate email matches session
    session_email = get_pending_verification_email(request)
    if not session_email or email != session_email:
        messages.error(request, "Invalid session. Please try again.")
        clear_pending_verification_email(request)
        return redirect("main:login")

    # Find user by email (username field stores email)
    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        messages.error(request, "No account found with this email address.")
        return redirect("main:login")

    # Check if user is already verified
    if user.is_active:
        messages.info(request, "Your account is already verified.")
        return redirect("main:login")

    # Check rate limit (cache-based, 60 seconds per email)
    # Check after confirming user exists and needs verification to prevent setting cooldown when no email will be sent
    allowed, remaining = check_email_resend_cooldown(email)
    if not allowed:
        messages.warning(request, f"Please wait {remaining} seconds before resending.")
        set_pending_verification_email(request, email)
        return redirect("main:verify_email_pending")

    # Send verification email
    send_verification_email(user, request)
    set_pending_verification_email(request, email)
    messages.success(request, "Verification email sent! Please check your inbox.")

    return redirect("main:verify_email_pending")
