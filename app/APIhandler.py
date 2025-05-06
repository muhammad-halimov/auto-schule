from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional, List

import requests
from config_local import api


@lru_cache(maxsize=100)
def cached_api_get(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API request failed: {e}")
        return None


class Student:
    def __init__(self, id, name, surname, patronymic, phone, email, contract, date_of_birth, roles, image):
        self.id = id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.phone = phone
        self.email = email
        self.contract = contract
        self.dateOfBirth = date_of_birth
        self.roles = roles
        self.image = image


class Admin:
    def __init__(self, email, username):
        self.email = email
        self.username = username


class Instructor:
    def __init__(self, id, name, surname, patronymic, phone, email, date_of_birth, drive_license, hire_date,
                 roles, image):
        self.id = id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.phone = phone
        self.email = email
        self.dateOfBirth = date_of_birth
        self.license = drive_license
        self.hireDate = hire_date
        self.roles = roles
        self.image = image


class Car:
    def __init__(self, id, car_mark, car_model, state_number, production_year, vin_number):
        self.id = id
        self.carMark = car_mark
        self.carModel = car_model
        self.stateNumber = state_number
        self.productionYear = production_year
        self.vinNumber = vin_number


class Teacher:
    def __init__(self, id, name, surname, patronymic, phone, email, date_of_birth, hire_date, roles, image):
        self.id = id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.phone = phone
        self.email = email
        self.dateOfBirth = date_of_birth
        self.hireDate = hire_date
        self.roles = roles
        self.image = image


class Course:
    def __init__(self, id, title, description, lessons):
        self.id = id
        self.title = title
        self.description = description
        self.lessons = lessons


class Lesson:
    def __init__(self, id, title, description, lesson_type, date):
        self.id = id
        self.title = title
        self.description = description
        self.lesson_type = lesson_type
        self.date = date


class Schedule:
    def __init__(self, id, time_from, time_to, days_of_week, notice, autodrome_id, category_id, instructor_id):
        self.id = id
        self.time_from = time_from
        self.time_to = time_to
        self.days_of_week = days_of_week
        self.notice = notice
        self.autodrome_id = autodrome_id
        self.category_id = category_id
        self.instructor_id = instructor_id


class Autodrome:
    def __init__(self, id, title, address, description):
        self.id = id
        self.title = title
        self.address = address
        self.description = description


class Category:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


teachers_list = []
instructors_list = []
cars_list = []
courses_list = []
schedule_list = []


def instructors() -> List[Instructor]:
    data = cached_api_get(f"{api}instructors")
    if not data:
        return []

    return [Instructor(
        item['id'],
        item['name'],
        item['surname'],
        item['patronym'],
        item['phone'],
        item['email'],
        item['dateOfBirth'],
        item['license'],
        item['hireDate'],
        item['roles'],
        item['image']
    ) for item in data]


def get_instructor_by_id(id: int) -> Optional[Instructor]:
    data = cached_api_get(f"{api}users/{id}")
    if not data:
        return None

    return Instructor(
        data['id'],
        data['name'],
        data['surname'],
        data['patronym'],
        data['phone'],
        data['email'],
        data['dateOfBirth'],
        data['license'],
        data['hireDate'],
        data['roles'],
        data.get('image')
    )


def teachers() -> List[Teacher]:
    data = cached_api_get(f"{api}teachers")
    if not data:
        return []

    return [Teacher(
        item['id'],
        item['name'],
        item['surname'],
        item['patronym'],
        item['phone'],
        item['email'],
        item['dateOfBirth'],
        item['hireDate'],
        item['roles'],
        item['image']
    ) for item in data]


def get_teacher_by_id(id: int) -> Optional[Teacher]:
    data = cached_api_get(f"{api}teachers/{id}")
    if not data:
        return None

    return Teacher(
        data['id'],
        data['name'],
        data['surname'],
        data['patronym'],
        data['phone'],
        data['email'],
        data['dateOfBirth'],
        data['hireDate'],
        data['roles'],
        data['image']
    )


def cars() -> List[Car]:
    data = cached_api_get(f"{api}cars")
    if not data:
        return []

    return [Car(
        item['id'],
        item['carMark']['title'],
        item['carModel'],
        item['stateNumber'],
        item['productionYear'],
        item['vinNumber']
    ) for item in data]


def get_car_by_id(id: int) -> Optional[Car]:
    data = cached_api_get(f"{api}cars/{id}")
    if not data:
        return None

    return Car(
        data['id'],
        data['carMark']['title'],
        data['carModel'],
        data['stateNumber'],
        data['productionYear'],
        data['vinNumber']
    )


def courses() -> List[Course]:
    data = cached_api_get(f"{api}courses")
    if not data:
        return []

    return [Course(
        item['id'],
        item['title'],
        item.get('description', ''),
        item.get('lessons', [])
    ) for item in data]


def get_course_by_id(id: int) -> Optional[Course]:
    data = cached_api_get(f"{api}courses/{id}")
    if not data:
        return None

    return Course(
        data['id'],
        data['title'],
        data.get('description', ''),
        data.get('lessons', [])
    )


def get_lesson_by_id(id: int) -> Optional[Lesson]:
    data = cached_api_get(f"{api}teacher_lessons/{id}")
    if not data:
        return None

    return Lesson(
        data['id'],
        data['title'],
        data['description'],
        data['type'],
        data['date']
    )


def user_is_authorized(id: int):
    data = cached_api_get(f"{api}users")
    if not data:
        return 0

    for user in data:
        if 'telegramId' in user and user['telegramId'] == str(id):
            if "ROLE_STUDENT" in user['roles']:
                return Student(
                    user['id'],
                    user['name'],
                    user['surname'],
                    user['patronym'],
                    user['phone'],
                    user['email'],
                    user['contract'],
                    user['dateOfBirth'],
                    user['roles'],
                    user['image']
                )
            elif "ROLE_ADMIN" in user['roles']:
                return Admin(
                    user['email'],
                    user['username']
                )
            elif "ROLE_TEACHER" in user['roles']:
                return Teacher(
                    user['id'],
                    user['name'],
                    user['surname'],
                    user['patronym'],
                    user['phone'],
                    user['email'],
                    user['dateOfBirth'],
                    user['hireDate'],
                    user['roles'],
                    user['image']
                )
            elif "ROLE_INSTRUCTOR" in user['roles']:
                return Instructor(
                    user['id'],
                    user['name'],
                    user['surname'],
                    user['patronym'],
                    user['phone'],
                    user['email'],
                    user['dateOfBirth'],
                    user['license'],
                    user['hireDate'],
                    user['roles'],
                    user['image']
                )
    return 0


def student_courses(telegram_id: int) -> List[Course]:
    data = cached_api_get(f"{api}students")
    if not data:
        return []

    list_courses = []
    for student in data:
        if 'telegramId' in student and student['telegramId'] == str(telegram_id):
            if 'courses' in student and isinstance(student['courses'], list):
                list_courses.extend([
                    Course(
                        c['id'],
                        c['title'],
                        c.get('description', ''),
                        c.get('lessons', [])
                    ) for c in student['courses']
                ])
    return list_courses


def update_user_data(user_id: int, surname: str, name: str, patronymic: str, password: str) -> int:
    users = cached_api_get(f"{api}users")
    if not users:
        return 0

    user_data = next((u for u in users if 'telegramId' in u and u['telegramId'] == str(user_id)), None)
    if not user_data:
        return 0

    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": user_data['email'], "password": password}
    )

    if auth_response.status_code != 200:
        return auth_response.status_code

    token = auth_response.json().get('token')
    if not token:
        return 0

    response = requests.patch(
        f"{api}users/{user_data['id']}",
        json={"surname": surname, "name": name, "patronym": patronymic},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/merge-patch+json"
        }
    )
    return response.status_code


def drive_schedules() -> List[Schedule]:
    data = cached_api_get(f"{api}drive_schedules")
    if not data:
        return []

    return [Schedule(
        item.get('id', 'N/A'),
        item.get('timeFrom', 'Не указано'),
        item.get('timeTo', 'Не указано'),
        item.get('daysOfWeek', []),
        item.get('notice', ''),
        item.get('autodrome', {}).get('id'),
        item.get('category', {}).get('id'),
        item.get('instructor', {}).get('id')
    ) for item in data]


def get_drive_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
    data = cached_api_get(f"{api}drive_schedules/{schedule_id}")

    if not data:
        return None

    return Schedule(
        id=data.get('id'),
        time_from=data.get('timeFrom', 'Не указано'),
        time_to=data.get('timeTo', 'Не указано'),
        days_of_week=data.get('daysOfWeek', []),
        notice=data.get('notice', ''),
        autodrome_id=data.get('autodrome', {}).get('id'),
        category_id=data.get('category', {}).get('id'),
        instructor_id=data.get('instructor', {}).get('id')
    )


def get_autodrome_by_id(id):
    data = cached_api_get(f"{api}autodromes/{id}")

    if not data:
        return Autodrome(id=id, title="Не удалось загрузить", address="Не удалось загрузить",
                         description="Не удалось загрузить")

    return Autodrome(
        id=data['id'],
        title=data.get('title', 'Не указано'),
        address=data.get('address', 'Не указан'),
        description=data.get('description', 'Не указано')
    )


def get_category_by_id(id):
    data = cached_api_get(f"{api}categories/{id}")

    if not data:
        return Category(id=id, title="Не удалось загрузить", description="Не удалось загрузить")

    return Category(
        id=data['id'],
        title=data.get('title', 'Не указано'),
        description=data.get('description', 'Не указано')
    )


def post_instructor_lesson(user_id, instructor_id, autodrome_id, category_id, date_time, password):
    users = cached_api_get(f"{api}users")
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
        json={"instructor": f"/api/users/{instructor_id}", "student": f"/api/users/{user_data['id']}",
              "date": f"{iso_format}", "autodrome": f"/api/autodromes/{autodrome_id}",
              "category": f"/api/categories/{category_id}"},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    return response.status_code
