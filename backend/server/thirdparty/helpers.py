import requests
import logging


logger = logging.getLogger(__name__)

def make_http_request(third_party_adapter, method, endpoint, data=None, requires_auth=True):
    """
    Makes a request to a Thirdparty API, handling authentication if needed.

    Args:
        adapter (Third party API Adapter): The initialized adapter instance.
        method (str): HTTP method ('GET', 'POST', etc.).
        endpoint (str): API endpoint.
        kwargs: Additional request parameters.

    Returns:
        dict: JSON response from the API.

    Raises:
        Exception: If the request fails.
    """
    headers = {}
    if requires_auth:
        
        # Check if token has expired and re - authenticate before making the request
        if(third_party_adapter.is_access_expired()):
            logger.info(f"{third_party_adapter.name} access expired. Re-gaining access ...")
            if not third_party_adapter.authenticate():
                return None

        headers["Authorization"] = f"{third_party_adapter.token_type} {third_party_adapter.access_token}"


    url = f"{third_party_adapter.base_url}{endpoint}"
    response = requests.request(method, url, json=data, headers=headers)

    try:
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        logger.info(f"Request to {url} failed: {err}")
        return None