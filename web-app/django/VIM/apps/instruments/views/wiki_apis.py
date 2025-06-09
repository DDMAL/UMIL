import requests
import urllib.parse
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse

WIKIDATA_URL = settings.WIKIDATA_URL
WIKIDATA_OAUTH_URL = settings.WIKIDATA_OAUTH_URL
WIKIDATA_REDIRECT_URI = settings.WIKIDATA_REDIRECT_URI
WIKIDATA_CLIENT_APP_KEY = settings.WIKIDATA_CLIENT_APP_KEY
WIKIDATA_CLIENT_APP_SECRET = settings.WIKIDATA_CLIENT_APP_SECRET

session = requests.Session()

def get_wikidata_access_token(request):
    access_token = request.COOKIES.get("wikidata_access_token")
    return JsonResponse({"access_token": access_token})


def wikidata_callback(request):
    # Retrieve the authorization code from the query parameters
    authorization_code = request.GET.get("code")
    if not authorization_code:
        return JsonResponse({"errors": "Authorization code not provided"}, status=400)
    # Exchange the authorization code for an access token
    base_url = f"{WIKIDATA_OAUTH_URL}/access_token"
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": WIKIDATA_CLIENT_APP_KEY,
        "client_secret": WIKIDATA_CLIENT_APP_SECRET,
        "redirect_uri": WIKIDATA_REDIRECT_URI,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = session.post(base_url, data=data, headers=headers)
    access_token = response.json().get("access_token")
    # Set token in an HTTP-only cookie
    response = redirect(request.session.pop("wikidata_next", "/"))
    if access_token:
        response.set_cookie(
            "wikidata_access_token",
            access_token,
            httponly=True,  # Prevent JavaScript access for security
            secure=True,  # Only send over HTTPS
            samesite="Lax",  # Prevent cross-site request forgery
        )
    return response

def wikidata_authorize(request):
    # Get the previous page (default to "/")
    next_url = request.GET.get("next", request.META.get("HTTP_REFERER", "/"))
    request.session["wikidata_next"] = next_url

    # Construct the authorization URL
    base_url = f"{WIKIDATA_OAUTH_URL}/authorize"
    params = {
        "response_type": "code",
        "client_id": WIKIDATA_CLIENT_APP_KEY,
        "redirect_uri": WIKIDATA_REDIRECT_URI,
    }
    authorization_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return redirect(authorization_url)