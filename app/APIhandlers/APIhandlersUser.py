from dataclasses import dataclass
from typing import Optional
import requests

from app.utils.jsons_creator import UserStorage
from config_local import api


@dataclass
class User:
    telegram_id: int
    db_id: int
    email: str
    password: str


def send_request(telegram_id, name, surname, phone, email, category):
    response = requests.post(
        f"{api}users", json={
            "name": f"{name}",
            "surname": f"{surname}",
            "phone": f"{phone}",
            "email": f"{email}",
            "telegramId": f"{telegram_id}",
            "category": f"/api/categories/{category}",
            "roles": ["ROLE_STUDENT"]
        },
        headers={
            "Content-Type": "application/json"
        })

    return response.status_code


def check_password(email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )
    return auth_response.status_code


def start(telegram_id: int):
    data = requests.get(f"{api}users").json()
    if not data:
        return 0

    for user in data:
        if not isinstance(user, dict):
            continue

        if 'telegramId' not in user or user.get('telegramId') != str(telegram_id):
            continue

        db_id = user.get('id')
        if not db_id:
            continue

        storage = UserStorage()
        user_obj = User(telegram_id=telegram_id,
                        db_id=db_id,
                        email=user.get('email', ''),
                        password="default_password")

        storage.set_user(
            telegram_id=telegram_id,
            db_id=db_id,
            email=user.get('email', ''),
            password="default_password"
        )

        return user_obj

    return 0


def update_user_data(user_id: int, surname: str, name: str, patronymic: str, email: str, password: str):
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

    data = {
        "surname": surname,
        "name": name,
        "patronym": patronymic
    }

    response = requests.patch(
        f"{api}users/{user_id}",
        headers=headers,
        json=data
    )
    return response.status_code


def find_user_by_telegram_id(telegram_id: int) -> Optional[int]:
    users_data = requests.get(f"{api}users").json()
    if not users_data:
        return 0

    for user in users_data:
        if not isinstance(user, dict):
            continue

        if 'telegramId' in user and user.get('telegramId') == str(telegram_id):
            db_id = user.get('id')
            print(db_id, "API")
            if db_id is None:
                return 0
            else:
                return db_id


def users():
    users_data = requests.get(f"{api}users").json()
    if not users_data:
        return 0

    users_list = []

    for user in users_data:
        if not isinstance(user, dict):
            continue

        users_list.append(user)
    return users_list


def get_user_by_id(user_id: int):
    user_data = requests.get(f"{api}users/{user_id}").json()
    if not user_data:
        return 0

    return user_data


def delete_user(user_id, email, password):
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

    delete_result = requests.delete(url=f"{api}users/{user_id}", headers=headers)
    return delete_result.status_code


def update_user_by_admin(user_id, name, surname, patronymic, email, password):

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
        "name": name,
        "surname": surname,
        "patronym": patronymic
    }

    url = f"{api}users/{user_id}"

    update_result = requests.patch(url=url, headers=headers, json=body)

    return update_result.status_code


def add_user_by_admin(role, name, surname, patronymic, email, password, admin_email, admin_password):

    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": admin_email, "password": admin_password}
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

    role_array = [role]
    print(role_array)

    body = {
        "name": name,
        "surname": surname,
        "patronym": patronymic,
        "email": email,
        "password": password,
        "roles": role_array
    }

    url = f"{api}users"

    update_result = requests.post(url=url, headers=headers, json=body)
    return update_result.status_code


def get_user_name(user_id):
    name = requests.get(f"{api}users/{user_id}").json().get('name', '')

    return name


def get_full_name(user_id):
    data = requests.get(f"{api}users/{user_id}").json()
    full_name = data.get('surname', '') + " " + data.get('name', '')

    return full_name


def get_user_role_by_id(user_id):
    print(user_id)
    role = requests.get(f"{api}users/{user_id}").json().get('roles')[0]

    return role


def approve_user_in_api(user_id, email, password):
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
        "isActive": True,
        "isApproved": True
    }

    return requests.patch(f"{api}users/{user_id}", headers=headers, json=body).status_code


def send_password_for_user_in_api(user_id, email, password):
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
        "Authorization": f"Bearer {token}"
    }

    result = requests.get(f"{api}create-password/{user_id}", headers=headers)

    return result.status_code


