import logging

from typing import Optional, Union
import requests

from app.APIhandlers.APIhandlersAdmin import Admin
from app.APIhandlers.APIhandlersInstructor import Instructor
from app.APIhandlers.APIhandlersStudent import Student
from app.APIhandlers.APIhandlersTeacher import Teacher
from app.utils.api_helpers import cached_api_get
from app.utils.jsons_creator import UserStorage
from config_local import api


def send_request(telegram_id, name, surname, phone, email, category):
    response = requests.post(f"{api}users",
                             json={
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


def start(telegram_id: int) -> Union[Student, Admin, Teacher, Instructor, int]:
    cached_api_get.cache_clear()
    data = cached_api_get(f"{api}users")
    if not data:
        return 0

    for user in data:
        if not isinstance(user, dict):
            continue

        if 'telegramId' not in user or user.get('telegramId') != str(telegram_id):
            continue

        if 'roles' not in user or not isinstance(user['roles'], list):
            continue

        db_id = user.get('id')
        if not db_id:
            continue

        storage = UserStorage()

        if "ROLE_STUDENT" in user['roles']:
            user_obj = Student(
                id=db_id,
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                contract=user.get('contract', ''),
                dateOfBirth=user.get('dateOfBirth', ''),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.jpg'),
                type='student'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
            return user_obj
        elif "ROLE_ADMIN" in user['roles']:
            user_obj = Admin(
                id=db_id,
                email=user.get('email', ''),
                username=user.get('username', ''),
                type='admin'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
            return user_obj
        elif "ROLE_TEACHER" in user['roles']:
            user_obj = Teacher(
                id=db_id,
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                dateOfBirth=user.get('dateOfBirth'),
                hireDate=user.get('hireDate'),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.jpg'),
                type='teacher'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
            return user_obj
        elif "ROLE_INSTRUCTOR" in user['roles']:
            user_obj = Instructor(
                id=db_id,
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                dateOfBirth=user.get('dateOfBirth'),
                license=user.get('license', ''),
                experience=user.get('experience'),
                hireDate=user.get('hireDate'),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.jpg'),
                type='instructor'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
            return user_obj
    return 0


def update_user_data(user_id: int, surname: str, name: str, patronymic: str, password: str) -> int:
    user_data = cached_api_get(f"{api}users/{user_id}")

    if not user_data or not isinstance(user_data, dict):
        return 0

    if 'email' not in user_data or 'id' not in user_data:
        return 0

    try:
        auth_response = requests.post(
            f"{api}authentication_token",
            json={"email": user_data['email'], "password": password},
            timeout=10
        )

        if auth_response.status_code != 200:
            return auth_response.status_code

        token = auth_response.json().get('token')
        if not token:
            return 0

        response = requests.patch(
            f"{api}users/{user_data['id']}",
            json={
                "surname": surname,
                "name": name,
                "patronym": patronymic
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/merge-patch+json"
            },
            timeout=10
        )
        return response.status_code

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return 0


def find_user_by_telegram_id(telegram_id: int) -> Optional[int]:
    users_data = cached_api_get(f"{api}users")
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
