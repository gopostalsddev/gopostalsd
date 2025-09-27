import requests
import logging
import time


logger = logging.getLogger(__name__)

def make_http_request(third_party_adapter, method, endpoint, data=None, requires_auth=True, max_retries=3, retry_delay=2, custom_base_url = None):
    """
    Makes a request to a Thirdparty API, handling authentication if needed.
    
    Args:
        third_party_adapter: The initialized adapter instance.
        method (str): HTTP method ('GET', 'POST', etc.).
        endpoint (str): API endpoint.
        data (dict, optional): Request body.
        requires_auth (bool): Whether authentication is required.
        max_retries (int): Number of times to retry on 429.
        retry_delay (int): Time (in seconds) to wait before retrying.
        base_url (str): custom base url
    Returns:
        dict: JSON response from the API, or None on failure.
    """
    headers = {}
    if requires_auth:
        # Check if token has expired and re-authenticate
        if third_party_adapter.is_access_expired():
            logger.info(f"{third_party_adapter.name} access expired. Re-gaining access ...")
            if not third_party_adapter.authenticate():
                return None
            
        headers["Authorization"] = third_party_adapter.access_token

    url = f"{third_party_adapter.base_url}{endpoint}" if custom_base_url is None else f"{custom_base_url}{endpoint}" #TODO: Add test for this

    # STATUS CODES FOR RETRY
    RATE_LIMIT_CODE = 429
    SERVER_ERROR_CODE = 500
    SERVER_UNAVAILABLE_CODE = 503  
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=10)
            
            if response.status_code == RATE_LIMIT_CODE:  # Rate limiting
                logger.warning(f"Rate limit hit, retrying in {retry_delay} seconds... ({attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                continue  # Retry the request
            
            if response.status_code == SERVER_ERROR_CODE: # Server error
                logger.warning(f"Server error, retrying in {retry_delay} seconds... ({attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                continue  # Retry the request

            if response.status_code == SERVER_UNAVAILABLE_CODE: # Service unavailable
                logger.warning(f"Server unavailable, retrying in {retry_delay} seconds... ({attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                continue  # Retry the request

            if response.status_code >= 400:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out.")
            return None
        except requests.RequestException as err:
            logger.error(f"Request to {url} failed: {err}")
            return None

    logger.error(f"Max retries reached for {url}")
    return None  # Return None after max retries