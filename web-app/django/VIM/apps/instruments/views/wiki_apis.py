""" This module contains functions to interact with the Wikidata API using OAuth. """

import requests
import urllib.parse
from django.shortcuts import redirect
from django.http import JsonResponse

WIKIDATA_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_OAUTH_URL = "https://www.wikidata.org/w/rest.php/oauth2"
WIKIDATA_REDIRECT_URI = "https://vim.simssa.ca/oauth/callback"
WIKIDATA_CLIENT_ID = "4b8617100ef01f44476115fb787d9d18"
session = requests.Session()


def wikidata_callback(request):
    print("[wikidata_callback] called")
    # Retrieve the authorization code from the query parameters
    authorization_code = request.GET.get("code")
    if not authorization_code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)
    # Exchange the authorization code for an access token
    base_url = f"{WIKIDATA_OAUTH_URL}/access_token"
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": WIKIDATA_CLIENT_ID,
        "redirect_uri": WIKIDATA_REDIRECT_URI,
    }

    response = requests.post(base_url, data=data, timeout=50)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        request.session["wikidata_access_token"] = access_token
        next_url = request.session.get("next", "/")
        return redirect(next_url)
    else:
        return JsonResponse({"error": response.json()}, status=response.status_code)


def wikidata_authorize(request):
    # Get the current target URL from the request
    next_url = request.GET.get("next", "/")
    request.session["next"] = next_url
    # Construct the authorization URL
    base_url = f"{WIKIDATA_OAUTH_URL}/authorize"
    params = {
        "response_type": "code",
        "client_id": WIKIDATA_CLIENT_ID,
        "redirect_uri": WIKIDATA_REDIRECT_URI,
    }
    authorization_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return redirect(authorization_url)


def add_info_to_wikidata_entity(action, access_token, wikidata_id, value, language):
    """
    Adds information to a Wikidata entity using OAuth.

    Args:
        action (str): The action to perform (e.g., "wbsetlabel", "wbsetdescription", "wbsetaliases").
        access_token (str): The OAuth access token.
        wikidata_id (str): The Wikidata ID of the entity.
        value (str): The value to add.
        language (str): The language code.

    Returns:
        dict: The response from the Wikidata API or an error message if failed.
    """
    try:
        params = {
            "action": action,
            "format": "json",
            "id": wikidata_id,
            "language": language,
            "tags": "wikidata-ui",
            "bot": 1,
            "errorformat": "plaintext",
            "uselang": "en",
        }
        if action == "wbsetaliases":
            params["add"] = value
        else:
            params["value"] = value

        # Authorization header with OAuth access token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = session.post(WIKIDATA_URL, data=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return {"error": f"Error adding label: {data['error']['info']}"}
        return data

    except requests.RequestException as e:
        return {"error": f"HTTP error occurred: {e}"}
    except ValueError as ve:
        return {"error": f"Value error occurred: {ve}"}
