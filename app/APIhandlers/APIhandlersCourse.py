from dataclasses import dataclass
from typing import List, Dict, Optional

import requests

from config_local import api


@dataclass
class Course:
    id: int
    title: str
    description: str
    category: Dict
    users: List[Dict]
    lessons: List[Dict]
    quizzes: List[Dict]


@dataclass
class Quiz:
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
    data = requests.get(f"{api}courses").json()
    if not data:
        return []

    return [
        Course(
            id=item['id'],
            title=item['title'],
            category=item.get('category', {}),
            description=item.get('description', ''),
            users=item.get('users', []),
            lessons=item.get('lessons', []),
            quizzes=item.get('quizzes', [])
        ) for item in data
    ]


def admin_courses() -> List[Course]:
    data = requests.get(f"{api}courses").json()
    if not data:
        return []

    return [
        Course(
            id=item['id'],
            title=item['title'],
            category=item.get('category', {}),
            description=item.get('description', ''),
            users=item.get('users', []),
            lessons=item.get('lessons', []),
            quizzes=item.get('quizzes', [])
        ) for item in data
    ]


def get_course_by_id(course_id: int) -> Optional[Course]:
    data = requests.get(f"{api}courses/{course_id}").json()
    if not data:
        return None

    return Course(
        id=data['id'],
        title=data['title'],
        category=data.get('category', {}),
        description=data.get('description', ''),
        users=data.get('users', []),
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
        "Authorization": f"Bearer {token}"
    }

    data = requests.get(f"{api}progress", headers=headers).json()

    if not data:
        return None

    for course in data['combinedProgress']['byCourse']:
        if course['courseId'] == course_id:
            return course['percentage']


def get_test_by_course_id(course_id):
    tests_data = requests.get(f"{api}course_quizzes").json()
    return [
        Quiz(
            id=test.get('id'),
            question=test.get('question'),
            answers=test.get('answers')
        )
        for test in tests_data
        if test.get('course', {}).get('id') == int(course_id)
    ]


def save_test_results(email: str, password: str, question_ids: List[int], answers: List[StudentAnswer]):
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

    results = []

    for question_id in question_ids:
        question_answers = [
            a.answer_id
            for a in answers if a.question_id == question_id
        ]

        if question_answers:
            results.append({
                "quizId": question_id,
                "answers": question_answers
            })
    try:
        response = requests.post(
            f"{api}progress/quiz/batch-update",
            headers=headers,
            json=results
        )
        return response.status_code
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None


def delete_course(course_id, email, password):
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

    delete_result = requests.delete(url=f"{api}courses/{course_id}", headers=headers)
    print(delete_result, delete_result.text)
    return delete_result.status_code


def get_all_quizzes():
    quizzes = requests.get(f"{api}course_quizzes").json()

    return [
        Quiz(
            id=test.get('id'),
            question=test.get('question'),
            answers=test.get('answers')
        )
        for test in quizzes
    ]


def get_quiz_title(quiz_id):
    quiz_title = requests.get(f"{api}course_quizzes/{quiz_id}").json().get('question', '')

    return quiz_title


def user_ids_in_course(course_id):
    course_users = requests.get(f"{api}courses/{course_id}").json()['users']

    ids_list = []

    for user in course_users:
        ids_list.append(user['id'])

    return ids_list


def update_course_in_api(course_id: int, title: str, description: str,
                         lessons: List, users: List, category: int,
                         quizzes: List, email: str, password: str):

    course_users = requests.get(f"{api}courses/{course_id}").json()['users']

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

    lessons_linked = []
    prefix_lesson = "api/teacher_lessons/"

    for lesson in lessons:
        lessons_linked.append(prefix_lesson + str(lesson))

    users_linked = []
    prefix_user = "api/users/"

    for user in users:
        users_linked.append(prefix_user + str(user))

    for course_user in course_users:
        users_linked.append(prefix_user + str(course_user['id']))

    quizzes_linked = []
    prefix_quiz = "api/course_quizzes/"

    for quiz in quizzes:
        quizzes_linked.append(prefix_quiz + str(quiz))

    body = {
        "id": course_id,
        "title": title,
        "description": description,
        "lessons": lessons_linked,
        "users": users_linked,
        "category": f"api/categories/{category}",
        "courseQuizzes": quizzes_linked
    }
    result = requests.patch(url=f"{api}courses/{course_id}", headers=headers, json=body)
    return result.status_code


def add_course_to_api(title: str, description: str,
                      lessons: List, users: List, category: int,
                      quizzes: List, email: str, password: str):

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

    lessons_linked = []
    prefix_lesson = "api/teacher_lessons/"
    if len(lessons) != 0:
        for lesson in lessons:
            lessons_linked.append(prefix_lesson + str(lesson))
    else:
        pass

    users_linked = []
    prefix_user = "api/users/"
    if len(users) != 0:
        for user in users:
            users_linked.append(prefix_user + str(user))
    else:
        pass

    quizzes_linked = []
    prefix_quiz = "api/course_quizzes/"
    if len(quizzes) != 0:
        for quiz in quizzes:
            quizzes_linked.append(prefix_quiz + str(quiz))
    else:
        pass

    body = {
        "title": title,
        "description": description,
        "lessons": lessons_linked,
        "users": users_linked,
        "category": f"api/categories/{category}",
        "courseQuizzes": quizzes_linked
    }
    result = requests.post(url=f"{api}courses", headers=headers, json=body)
    return result.status_code
