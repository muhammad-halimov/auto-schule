from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

import requests

from config_local import api


@dataclass
class DriveLesson:
    id: int
    instructor: Dict
    student: Dict
    date: str
    autodrome: Dict
    category: Dict


def post_instructor_lesson(user_id: int, instructor_id: int, autodrome_id: int,
                           category_id: int, date_time: str, password: str) -> int:
    users = requests.get(f"{api}users").json()
    if not users:
        return 0

    user_data = next((u for u in users if 'telegramId' in u and u['telegramId'] == str(user_id)), None)
    if not user_data:
        return 0

    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": user_data['email'], "password": password}
    )

    token = auth_response.json().get('token')
    if not token:
        return 0

    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    dt_utc = dt.replace(tzinfo=timezone.utc)
    iso_format = dt_utc.isoformat(timespec='milliseconds')

    response = requests.post(
        f"{api}instructor_lessons",
        json={
            "instructor": f"/api/users/{instructor_id}",
            "student": f"/api/users/{user_data['id']}",
            "date": f"{iso_format}",
            "autodrome": f"/api/autodromes/{autodrome_id}",
            "category": f"/api/categories/{category_id}"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    return response.status_code


def get_instructor_lessons(email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = requests.get(f"{api}instructor_lessons", headers=headers).json()
    lessons_list = []

    for lesson in data:
        lessons_list.append(DriveLesson(
            id=lesson.get('id'),
            instructor=lesson.get('instructor'),
            student=lesson.get('student'),
            date=lesson.get('date'),
            autodrome=lesson.get('autodrome'),
            category=lesson.get('category')
        ))

    return lessons_list


def get_instructor_lesson_by_id(lesson_id, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    lesson = requests.get(f"{api}instructor_lessons/{lesson_id}", headers=headers).json()

    return DriveLesson(
        id=lesson.get('id'),
        instructor=lesson.get('instructor'),
        student=lesson.get('student'),
        date=lesson.get('date'),
        autodrome=lesson.get('autodrome'),
        category=lesson.get('category')
    )


def delete_instructor_lesson_from_api(lesson_id, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    result = requests.delete(f"{api}instructor_lessons/{lesson_id}", headers=headers)

    return result.status_code


def create_instructor_lesson(lesson_data, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    result = requests.post(f"{api}instructor_lessons", headers=headers, json=lesson_data)

    return result.status_code


def update_instructor_lesson(lesson_data: dict, email: str, password: str):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/merge-patch+json"
    }

    response = requests.patch(f"{api}instructor_lessons/{lesson_data.get('id')}", headers=headers, json=lesson_data)
    return response.status_code
