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
    quizzes: List[Dict]


@dataclass
class Test:
    id: int
    question: str
    answers: List[Dict]


@dataclass
class StudentAnswer:
    question_id: int
    question_text: str
    answer_id: int
    answer_text: str
    is_correct: bool


def courses() -> List[Course]:
    data = cached_api_get(f"{api}courses")
    if not data:
        return []

    return [
        Course(
            id=item['id'],
            title=item['title'],
            description=item.get('description', ''),
            lessons=item.get('lessons', []),
            quizzes=item.get('quizzes', [])
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
        lessons=data.get('lessons', []),
        quizzes=data.get('courseQuizzes', [])
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


def get_test_by_course_id(course_id):
    tests_data = cached_api_get(f"{api}course_quizzes")
    print(course_id)
    print(tests_data)
    return [
        Test(
            id = test.get('id'),
            question=test.get('question'),
            answers=test.get('answers')
        )
        for test in tests_data
        if test['course']['id'] == int(course_id)
    ]


async def save_test_results(email: str, password: str, question_ids: List[int], answers: List[StudentAnswer]):
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

    data = {}

    i = 0

    for a in answers:
        data = {
            "question_ids": a.question_id,
            "answers": [{
                "answer_id": a.answer_id
            }]
        }

    response = requests.post(f"{api}progress/quiz/update", headers=headers, json=data)
    return response.json()
