from dataclasses import dataclass

import requests

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Category:
    id: int
    title: str
    description: str


def categories():
    data = cached_api_get(f"{api}categories")
    if not data:
        return []

    return [
        Category(
            id=item['id'],
            title=item['title'],
            description=item['description']
        ) for item in data
    ]


def admin_categories():
    data = requests.get(f"{api}categories").json()
    if not data:
        return []

    return [
        Category(
            id=item['id'],
            title=item['title'],
            description=item['description']
        ) for item in data
    ]


def get_category_by_id(category_id: int):
    data = cached_api_get(f"{api}categories/{category_id}")

    if not data:
        return None

    return Category(
        id=data['id'],
        title=data.get('title', 'Не указано'),
        description=data.get('description', 'Не указано')
    )


def get_admin_category_by_id(category_id: int):
    data = requests.get(f"{api}categories/{category_id}").json()

    if not data:
        return None

    return Category(
        id=data['id'],
        title=data.get('title', 'Не указано'),
        description=data.get('description', 'Не указано')
    )


def add_category_to_api(title: str, description: str, email: str, password: str) -> int:
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        return auth_response.status_code

    token = auth_response.json().get('token')
    if not token:
        return 401

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{api}categories",
        headers=headers,
        json={
            "title": title,
            "description": description
        }
    )

    return response.status_code


def delete_category(category_id, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        return auth_response.status_code

    token = auth_response.json().get('token')
    if not token:
        return 401

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    result = requests.delete(url=f"{api}categories/{category_id}", headers=headers)

    return result.status_code


def update_category_in_api(category_id: int, title: str, description: str, email: str, password: str) -> int:
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        return auth_response.status_code

    token = auth_response.json().get('token')
    if not token:
        return 401

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/merge-patch+json"
    }

    body = {
        "title": title,
        "description": description
    }

    response = requests.patch(
        f"{api}categories/{category_id}",
        headers=headers,
        json=body
    )

    return response.status_code