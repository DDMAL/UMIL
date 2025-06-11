import requests
import urllib.parse
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from VIM.apps.instruments.models import InstrumentName

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

def add_info_to_wikidata_entity(action, access_token, wikidata_id, value, language):
    """
    Adds information to a Wikidata entity using OAuth.

    Args:
        action (str): The action to perform (e.g., "add_label", "add_description", "add_aliases").
        access_token (str): The OAuth access token.
        wikidata_id (str): The Wikidata ID of the entity.
        value (str): The value to add.
        language (str): The language code.

    Returns:
        dict: The response from the Wikidata API or an error message if failed.
    """
    try:
        # Authorization header with OAuth access token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        if action == "label":
            body = {"label": value}
            url = f"{WIKIDATA_URL}/entities/items/{wikidata_id}/labels/{language}"
        elif action == "alias":
            body = {"aliases": [value]}
            url = f"{WIKIDATA_URL}/entities/items/{wikidata_id}/aliases/{language}"
        else:
            return {"errors": f"Invalid action: {action}"}  # Invalid action

        if action == "add_aliases":
            response = session.post(url, headers=headers, json=body)
        else:
            response = session.put(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        if "errorKey" in data:
            return {
                "errors": f"Error adding label to Wikidata: {data['messageTranslations']['en']}"
            }
        return data

    except requests.RequestException as e:
        return {"errors": f"HTTP error occurred: {e}"}
    except ValueError as ve:
        return {"errors": f"Value error occurred: {ve}"}
    
def edit_wikidata(request):
    """
    This method is intended to be called to edit Wikidata entries for verified instrument names.
    It can be triggered by a button in the template.
    """
        # retrieve all instrument names that are currently verified
    verified = InstrumentName.objects.filter(status="verified")
    access_token = get_wikidata_access_token(request)

    for instrument_name in verified:
        print(f"Processing instrument name: {instrument_name.name} in language {instrument_name.language}")
        # # post to wikidata
        # if instrument_name.is_alias:
        #     add_info_to_wikidata_entity("alias", access_token, instrument_name.instrument.wikidata_id, instrument_name.name, instrument_name.language)
        # else:
        #     add_info_to_wikidata_entity("label", access_token, instrument_name.instrument.wikidata_id, instrument_name.name, instrument_name.language)

    InstrumentName.objects.filter(status="verified").update(
        status="uploaded"
    )