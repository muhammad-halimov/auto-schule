from dataclasses import dataclass

import requests

from config_local import api


@dataclass
class Category:
    id: int
    title: str
    master_title: str
    description: str
    price: int
    type: str


def categories():
    data = requests.get(f"{api}categories").json()
    if not data:
        return []

    return [
        Category(
            id=item.get('id'),
            title=item.get('title', ''),
            master_title=item.get('masterTitle', ''),
            description=item.get('description'),
            price=item.get('price'),
            type=item.get('type', '')
        ) for item in data
    ]


def admin_categories():
    data = requests.get(f"{api}categories").json()
    if not data:
        return []

    return [
        Category(
            id=item.get('id'),
            title=item.get('title', ''),
            master_title=item.get('masterTitle', ''),
            description=item.get('description'),
            price=item.get('price'),
            type=item.get('type', '')
        ) for item in data
    ]


def admin_categories_course():
    data = requests.get(f"{api}categories").json()
    if not data:
        return []

    category_list = []

    for category in data:
        if category.get('type') == "course":
            category_list.append(Category(
                id=category.get('id'),
                title=category.get('title'),
                master_title=category.get('masterTitle'),
                description=category.get('description'),
                price=category.get('price'),
                type=category.get('type')
            ))

    return category_list


def admin_categories_schedule():
    data = requests.get(f"{api}categories").json()
    if not data:
        return []

    category_list = []

    for category in data:
        if category.get('type') == "driving":
            category_list.append(Category(
                id=category.get('id'),
                title=category.get('title'),
                master_title=category.get('masterTitle'),
                description=category.get('description'),
                price=category.get('price'),
                type=category.get('type')
            ))

    return category_list


def get_category_by_id(category_id: int):
    data = requests.get(f"{api}categories/{category_id}").json()

    if not data:
        return None

    return Category(
        id=data.get('id'),
        title=data.get('title', ''),
        master_title=data.get('masterTitle', ''),
        description=data.get('description'),
        price=data.get('price'),
        type=data.get('type', '')
    )


def get_admin_category_by_id(category_id: int):
    data = requests.get(f"{api}categories/{category_id}").json()

    if not data:
        return None

    return Category(
        id=data.get('id'),
        title=data.get('title', ''),
        master_title=data.get('masterTitle', ''),
        description=data.get('description'),
        price=data.get('price'),
        type=data.get('type', '')
    )


def add_category_to_api(category_data, email: str, password: str) -> int:
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
        json=category_data
    )
    print(response.status_code, response.text)

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


def update_category_in_api(category_id: int, data, email: str, password: str) -> int:
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

    response = requests.patch(
        f"{api}categories/{category_id}",
        headers=headers,
        json=data
    )
    print(response.status_code, response.text)
    return response.status_code


def get_price_by_category_id(category_id):
    price = requests.get(f"{api}categories/{category_id}").json()

    return price.get('price')
