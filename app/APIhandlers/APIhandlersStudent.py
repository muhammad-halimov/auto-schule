from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests

from app.APIhandlers.APIhandlersCourse import Course
from app.APIhandlers.APIhandlersDriveLesson import DriveLesson
from app.utils.api_helpers import cached_api_get, cached_api_get_with_headers

from config_local import api


@dataclass
class Student:
    id: int
    name: str
    surname: str
    patronymic: str
    phone: str
    email: str
    contract: str
    dateOfBirth: str
    roles: List[str]
    image: str
    type: str


def student_courses(student_id: int) -> List[Course]:
    data = cached_api_get(f"{api}students/{student_id}")
    if not data:
        return []

    list_courses = []
    if isinstance(data, dict) and 'courses' in data and isinstance(data['courses'], list):
        list_courses.extend([
            Course(
                id=c['id'],
                title=c['title'],
                description=c.get('description', ''),
                lessons=c.get('lessons', []),
                quizzes=c.get('quzzes', [])
            ) for c in data['courses'] if isinstance(c, dict)
        ])
    return list_courses


def my_schedules(student_id: int, email: str, password: str) -> list[DriveLesson] | int:
    try:
        auth_response = requests.post(
            f"{api}authentication_token",
            json={"email": email, "password": password}
        )

        if auth_response.status_code != 200:
            print(f"Authentication failed: {auth_response.status_code}")
            return 0

        auth_data = auth_response.json()
        token = auth_data.get('token')
        if not token:
            print("No token in auth response")
            return 0

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        my_schedules_list = cached_api_get_with_headers(
            url=f"{api}instructor_lessons",
            headers=headers
        )

        if not my_schedules_list:
            return 0

        result = []
        for item in my_schedules_list:
            if item.get('student', {}).get('id') != student_id:
                continue

            date_str = item.get('date', '')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    pass

            lesson = DriveLesson(
                id=item.get('id', 0),
                instructor={
                    'id': item.get('instructor', {}).get('id', 0),
                    'name': item.get('instructor', {}).get('name', ''),
                    'surname': item.get('instructor', {}).get('surname', '')
                },
                date=date_str,
                autodrome={
                    'id': item.get('autodrome', {}).get('id', 0),
                    'title': item.get('autodrome', {}).get('title', '')
                },
                category={
                    'id': item.get('category', {}).get('id', 0),
                    'title': item.get('category', {}).get('title', ''),
                    'price': item.get('category', {}).get('price', {}).get('price', 0)
                }
            )
            result.append(lesson)

        return result if result else 0

    except Exception as e:
        print(f"Error in my_schedules: {e}")
        return 0


def get_my_schedule_by_id(schedule_id, email, password):

    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return 0

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return 0

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    schedule_data = cached_api_get_with_headers(url=f"{api}instructor_lessons/{schedule_id}", headers=headers)
    if not schedule_data:
        return 0

    else:
        date_str = schedule_data.get('date', '')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                pass

        return DriveLesson(
            id=schedule_data.get('id', 0),
            instructor={
                'id': schedule_data.get('instructor', {}).get('id', 0),
                'name': schedule_data.get('instructor', {}).get('name', ''),
                'surname': schedule_data.get('instructor', {}).get('surname', '')
            },
            date=date_str,
            autodrome={
                'id': schedule_data.get('autodrome', {}).get('id', 0),
                'title': schedule_data.get('autodrome', {}).get('title', '')
            },
            category={
                'id': schedule_data.get('category', {}).get('id', 0),
                'title': schedule_data.get('category', {}).get('title', ''),
                'price': schedule_data.get('category', {}).get('price', {}).get('price', 0)
            }
        )


def cancel_lesson_by_id(lesson_id, email, password):

    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return 0

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return 0

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.delete(f"{api}instructor_lessons/{lesson_id}", headers=headers)
    return response.status_code


def check_time_lessons(instructor_id, date, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return []

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    lessons_data = cached_api_get_with_headers(url=f"{api}instructor_lessons", headers=headers)

    taked_time = []

    for lesson in lessons_data:
        lesson_date_str = lesson.get('date', '')
        if lesson_date_str:
            try:
                dt = datetime.fromisoformat(lesson_date_str.replace('Z', '+00:00'))
                lesson_date = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%H:%M')
                if lesson.get('instructor', {}).get('id', 0) == instructor_id and lesson_date == date:
                    taked_time.append(time_str)
            except ValueError:
                continue
    return taked_time
