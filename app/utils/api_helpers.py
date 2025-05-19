import requests


def cached_api_get(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API request failed: {e}")
        return None


def cached_api_get_with_headers(url: str, headers: dict):
    try:
        response = requests.get(
            url=url,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
        return None
