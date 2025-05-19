from dataclasses import dataclass
from typing import Optional, List, Dict

import requests

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Lesson:
    id: int
    title: str
    description: str
    lesson_type: str
    date: str
    videos: List[Dict]

def get_all_lessons():
    data = cached_api_get(f"{api}teacher_lessons/")

    lessons_list = []

    for lesson in data:
        lessons_list.append(Lesson(id=lesson.get('id'),
                                   title=lesson.get('title', ''),
                                   description=lesson.get('description', ''),
                                   lesson_type=lesson.get('lesson_type', ''),
                                   date=lesson.get('date', ''),
                                   videos=lesson.get('videos')
                                   ))
    return lessons_list


def get_lesson_by_id(lesson_id: int) -> Optional[Lesson]:
    data = cached_api_get(f"{api}teacher_lessons/{lesson_id}")
    if not data:
        return None

    return Lesson(
        id=data['id'],
        title=data['title'],
        description=data['description'],
        lesson_type=data['type'],
        date=data['date'],
        videos=data['videos']
    )


def lesson_marked(lesson_id, email, password):
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

    body = {
        "lessonId": lesson_id
    }

    lessons_marked = requests.post(url=f"{api}progress/lesson/update", headers=headers, json=body)
    print(lessons_marked.status_code, lesson_id)
    print(lessons_marked.text)
    return lessons_marked.status_code


def get_lesson_title(lesson_id):
    lesson_title = requests.get(f"{api}teacher_lessons/{lesson_id}").json().get('title', '')

    return lesson_title