from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests

from app.APIhandlers.APIhandlersCourse import Course
from app.APIhandlers.APIhandlersDriveLesson import DriveLesson
from app.APIhandlers.APIhandlersInstructor import instructors

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


def get_all_students():
    students = requests.get(f"{api}students").json()
    if not students:
        return []

    students_list = []

    for student in students:
        students_list.append(Student(
          id=student.get('id'),
          name=student.get('name'),
          surname=student.get('surname'),
          patronymic=student.get('patronym'),
          phone=student.get('phone'),
          email=student.get('email'),
          contract=student.get('contract'),
          dateOfBirth=student.get('dateOfBirth'),
          roles=student.get('roles'),
          image=student.get('image'),
          type=student.get('type')
        ))

    return students_list


def student_courses(student_id: int) -> List[Course]:
    data = requests.get(f"{api}students/{student_id}").json()
    if not data:
        return []

    list_courses = []
    if isinstance(data, dict) and 'courses' in data and isinstance(data['courses'], list):
        list_courses.extend([
            Course(
                id=c['id'],
                title=c['title'],
                category=c.get('category', {}),
                description=c.get('description', ''),
                users=c.get('users', []),
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

        my_schedules_list = requests.get(
            url=f"{api}instructor_lessons",
            headers=headers
        ).json()

        if not my_schedules_list:
            return 0

        result = []
        for item in my_schedules_list:
            if item.get('student', {}).get('id') != student_id:
                continue

            lesson = DriveLesson(
                id=item.get('id', 0),
                instructor=item.get("instructor"),
                student=item.get("student"),
                date=item.get('date', ''),
                autodrome=item.get("autodrome"),
                category=item.get("category")
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

    schedule_data = requests.get(url=f"{api}instructor_lessons/{schedule_id}", headers=headers).json()
    if not schedule_data:
        return 0

    else:

        return DriveLesson(
            id=schedule_data.get('id', 0),
            instructor=schedule_data.get('instructor'),
            student=schedule_data.get('student'),
            date=schedule_data.get('date', ''),
            autodrome=schedule_data.get('autodrome'),
            category=schedule_data.get('category')
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

    lessons_data = requests.get(url=f"{api}instructor_lessons", headers=headers).json()

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


def get_student_progress_by_id(student_id, email, password):
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

    data = requests.get(f"{api}progress/student/{student_id}", headers=headers).json()
    if not data:
        return {}

    return data


def get_balance_by_id(student_id):
    return requests.get(f"{api}users/{student_id}").json().get('balance', 0)


def get_courses_sign_up(user_id):
    student_courses_list = requests.get(f"{api}users/{user_id}").json().get('courses')
    ids_list = []

    for course in student_courses_list:
        ids_list.append(course.get('id'))

    courses = requests.get(f"{api}courses").json()
    course_list = []

    for course in courses:
        if course.get('id') not in ids_list:
            course_list.append(course)

    return course_list


def sign_up_course(course_id, user_id, email, password):
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
        "Content-Type": "application/merge-patch+json"
    }

    header_post = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    course = requests.get(f"{api}courses/{course_id}").json()

    course_users = course.get('users')

    student = requests.get(f"{api}users/{user_id}").json()

    balance = student.get('balance', 0)

    user_ids_list = [f"api/users/{student.get('id')}"]

    for user in course_users:
        user_ids_list.append(f"api/users/{user.get('id')}")

    user_json = {
        "users": user_ids_list
    }

    transaction_json = {
        "user": f"api/users/{user_id}",
        "course": f"api/courses/{course_id}"
    }

    if course.get('category').get('price') > balance:
        return 0
    else:
        result = requests.patch(f"{api}courses/{course_id}", headers=headers, json=user_json)
        balance_json = {
            "balance": f"{balance - course.get('category').get('price')}"
        }
        requests.patch(f"{api}users/{user_id}", headers=headers, json=balance_json)
        requests.post(f"{api}transactions", headers=header_post, json=transaction_json)
        print(requests.post(f"{api}transactions", headers=header_post, json=transaction_json).status_code)
        return result.status_code


def get_all_transaction(user_id, email, password):
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
        "Authorization": f"Bearer {token}"
    }

    result = requests.get(f"{api}transactions_filtered/{user_id}", headers=headers).json()

    return result


def get_transaction_by_id_from_api(transaction_id, email, password):
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
        "Authorization": f"Bearer {token}"
    }

    result = requests.get(f"{api}transactions/{transaction_id}", headers=headers).json()

    return result


def fill_balance_in_api(amount, user_id, email, password):
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
        "Content-Type": "application/merge-patch+json"
    }

    amount_json = {
        "balance": f"{amount}"
    }

    result = requests.patch(url=f"{api}users/{user_id}", headers=headers, json=amount_json)
    print(result.status_code, result.text)
    return result.status_code