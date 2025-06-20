import json
from dataclasses import dataclass
from typing import List, Optional

import requests

from app.APIhandlers.APIhandlersCourse import Course, Quiz
from app.APIhandlers.APIhandlersLesson import Lesson
from config_local import api


@dataclass
class Teacher:
    id: int
    name: str
    surname: str
    patronymic: str
    phone: str
    email: str
    dateOfBirth: str
    hireDate: str
    roles: List[str]
    image: str
    type: str


def teachers() -> List[Teacher]:
    data = requests.get(f"{api}teachers").json()
    if not data:
        return []

    return [
        Teacher(
            id=item['id'],
            name=item['name'],
            surname=item['surname'],
            patronymic=item.get('patronym', ''),
            phone=item['phone'],
            email=item['email'],
            dateOfBirth=item['dateOfBirth'],
            hireDate=item['hireDate'],
            roles=item['roles'],
            image=item.get('image', 'static/img/default.jpg'),
            type='teacher'
        ) for item in data
    ]


def get_teacher_by_id(teacher_id: int) -> Optional[Teacher]:
    data = requests.get(f"{api}users/{teacher_id}").json()
    if not data:
        return None

    return Teacher(
        id=data['id'],
        name=data['name'],
        surname=data['surname'],
        patronymic=data.get('patronym', ''),
        phone=data['phone'],
        email=data['email'],
        dateOfBirth=data['dateOfBirth'],
        hireDate=data['hireDate'],
        roles=data['roles'],
        image=data.get('image', 'static/img/default.jpg'),
        type='teacher'
    )


def get_teacher_courses(teacher_id):
    courses = requests.get(f"{api}courses").json()
    if not courses:
        return []

    courses_list = []

    for course in courses:
        for lesson in course.get('lessons'):
            if lesson.get('teacher').get('id') == teacher_id:
                courses_list.append(Course(id=course.get('id'),
                                    title=course.get('title'),
                                    category=course.get('category', {}),
                                    description=course.get('description', ''),
                                    users=course.get('users', []),
                                    lessons=course.get('lessons', []),
                                    quizzes=course.get('quizzes', [])))
                break

    return courses_list


def get_teacher_lessons(teacher_id):
    courses = requests.get(f"{api}courses").json()
    if not courses:
        return []

    lessons_list = []

    for course in courses:
        if 'lessons' not in course or not course['lessons']:
            continue

        for lesson in course['lessons']:
            if lesson.get('teacher') and lesson['teacher'].get('id') == teacher_id:
                lessons_list.append(Lesson(
                    id=lesson.get('id'),
                    title=lesson.get('title', ''),
                    description=lesson.get('description', ''),
                    lesson_type=lesson.get('type', ''),
                    date=lesson.get('date', ''),
                    videos=lesson.get('videos', [])
                ))

    return lessons_list


def get_teacher_quizzes():
    quizzes = requests.get(f"{api}course_quizzes").json()
    if not quizzes:
        return []

    quizzes_list = []

    for quiz in quizzes:
        quizzes_list.append(Quiz(
            id=quiz['id'],
            question=quiz['question'],
            answers=quiz['answers']))

    return quizzes_list


def get_quiz_by_id(quiz_id):
    quiz = requests.get(f"{api}course_quizzes/{quiz_id}").json()

    return Quiz(id=quiz['id'],
                question=quiz['question'],
                answers=quiz['answers'])


def delete_quiz_from_api(quiz_id, email, password):
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

    result = requests.delete(url=f"{api}course_quizzes/{quiz_id}", headers=headers)

    return result.status_code


def create_quiz(quiz, answers, email, password):
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

    result = requests.post(url=f"{api}course_quizzes", headers=headers, json=quiz)

    question_id = int(json.loads(result.text).get('id'))

    for answer in answers.get('answers'):
        answer_json = {
            "answerText": answer.get('answerText'),
            "status": answer.get('status'),
            "courseQuiz": f"api/course_quizzes/{question_id}"
        }
        requests.post(url=f"{api}course_quiz_answers", headers=headers, json=answer_json)

    return result.status_code


def update_question_in_api(email, password, quiz_data):
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

    quiz = {
        'question': quiz_data.get('question_text')
    }

    result = requests.patch(url=f"{api}course_quizzes/{int(quiz_data.get('id'))}", headers=headers, json=quiz)

    question_id = int(quiz_data.get('id'))

    for answer in quiz_data.get('answers'):
        answer_json = {
            "answerText": answer.get('answerText'),
            "status": answer.get('status'),
            "courseQuiz": f"api/course_quizzes/{question_id}"
        }
        requests.patch(url=f"{api}course_quiz_answers/{answer.get('id')}", headers=headers, json=answer_json)

    return result.status_code
