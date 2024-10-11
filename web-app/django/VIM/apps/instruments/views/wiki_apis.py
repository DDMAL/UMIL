""" This module contains functions to interact with the Wikidata API. """

import requests

WIKIDATA_URL = "https://www.wikidata.org/w/api.php"

session = requests.Session()


def get_csrf_token(username, password, url=WIKIDATA_URL):
    """
    Logs in to Wikidata.

    Args:
        username (str): The username of the account.
        password (str): The password of the account.

    Returns:
        tuple: The CSRF token and username if successful,
            otherwise (None, None, error_message).
    """
    try:
        # Step 1: Retrieve a login token
        params_1 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json",
        }
        response = session.get(url=url, params=params_1)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        if "query" not in data or "tokens" not in data["query"]:
            raise ValueError("Failed to retrieve login token.")
        login_token = data["query"]["tokens"]["logintoken"]
        print(f"login_token: {login_token}")

        # Step 2: Send a post request to login
        params_2 = {
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "format": "json",
            "lgtoken": login_token,
        }
        response = session.post(url, data=params_2)
        response.raise_for_status()
        data = response.json()
        if data.get("login", {}).get("result") != "Success":
            raise ValueError(
                f"Login failed: {data.get('login', {}).get('reason', 'Unknown error')}"
            )

        lgusername = data["login"]["lgusername"]
        print(f"lgusername: {lgusername}")

        # Obtain a CSRF token
        params_3 = {
            "action": "query",
            "meta": "tokens",
            "format": "json",
            "type": "csrf",
            "assertuser": lgusername,
        }
        response = session.get(url=url, params=params_3)
        response.raise_for_status()
        data = response.json()
        if "query" not in data or "tokens" not in data["query"]:
            raise ValueError("Failed to retrieve CSRF token.")
        csrf_token = data["query"]["tokens"]["csrftoken"]
        print(f"csrf_token: {csrf_token}")
        return csrf_token, lgusername, None

    except requests.RequestException as e:
        return None, None, f"HTTP error occurred: {e}"
    except ValueError as ve:
        return None, None, f"Value error occurred: {ve}"


def add_info_to_wikidata_entity(
    action, csrf_token, wikidata_id, value, language, username
):
    """
    Adds an existing Wikimedia image to a Wikidata entity.

    Args:
        action (str): The action to perform
            (e.g., "wbsetlabel", "wbsetdescription", "wbsetaliases").
        csrf_token (str): The CSRF token.
        wikidata_id (str): The Wikidata ID of the entity.
        value (str): The value to add.
        language (str): The language code.
        username (str): The username of the account.

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
            "assertuser": username,
            "errorformat": "plaintext",
            "uselang": "en",
            "token": csrf_token,
        }
        if action == "wbsetaliases":
            params["add"] = value
        else:
            params["value"] = value

        response = session.post(WIKIDATA_URL, data=params)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return {"error": f"Error adding label: {data['error']['info']}"}
        return data

    except requests.RequestException as e:
        return {"error": f"HTTP error occurred: {e}"}
    except ValueError as ve:
        return {"error": f"Value error occurred: {ve}"}
