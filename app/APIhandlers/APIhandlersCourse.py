from dataclasses import dataclass
from typing import List, Dict, Optional

import requests

from app.utils.api_helpers import cached_api_get, cached_api_get_with_headers
from config_local import api


@dataclass
class Course:
    id: int
    title: str
    description: str
    lessons: List[Dict]


def courses() -> List[Course]:
    data = cached_api_get(f"{api}courses")
    if not data:
        return []

    return [
        Course(
            id=item['id'],
            title=item['title'],
            description=item.get('description', ''),
            lessons=item.get('lessons', [])
        ) for item in data
    ]


def get_course_by_id(id: int) -> Optional[Course]:
    data = cached_api_get(f"{api}courses/{id}")
    if not data:
        return None

    return Course(
        id=data['id'],
        title=data['title'],
        description=data.get('description', ''),
        lessons=data.get('lessons', [])
    )


def get_courses_progress_by_id(course_id, email, password):
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

    data = cached_api_get_with_headers(f"{api}progress", headers=headers)

    if not data:
        return None

    for course in data['lessons']['progress']['byCourse']:
        if course['courseId'] == course_id:
            return course['percentage']

