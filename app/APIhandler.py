import logging
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional, List, Dict, Union
from dataclasses import dataclass
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


@dataclass
class Admin:
    email: str
    username: str


@dataclass
class Instructor:
    id: int
    name: str
    surname: str
    patronymic: str
    phone: str
    email: str
    dateOfBirth: str
    license: str
    hireDate: str
    roles: List[str]
    image: str


@dataclass
class Car:
    id: int
    carMark: str
    carModel: str
    stateNumber: str
    productionYear: str
    vinNumber: str


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


@dataclass
class Course:
    id: int
    title: str
    description: str
    lessons: List[Dict]


@dataclass
class Lesson:
    id: int
    title: str
    description: str
    lesson_type: str
    date: str


@dataclass
class Schedule:
    id: int
    time_from: str
    time_to: str
    days_of_week: List[str]
    notice: str
    autodrome_id: Optional[int]
    category_id: Optional[int]
    instructor_id: Optional[int]


@dataclass
class Autodrome:
    id: int
    title: str
    address: str
    description: str


@dataclass
class Category:
    id: int
    title: str
    description: str


# Хранилище пользовательских данных
class UserStorage:
    _instance = None
    _users: Dict[int, Union[Student, Admin, Teacher, Instructor]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_user(cls, user_id: int) -> Optional[Union[Student, Admin, Teacher, Instructor]]:
        return cls._users.get(user_id)

    @classmethod
    def set_user(cls, user_id: int, user_data: Union[Student, Admin, Teacher, Instructor]):
        cls._users[user_id] = user_data

    @classmethod
    def clear_user(cls, user_id: int):
        cls._users.pop(user_id, None)


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

    print(telegram_id, name, surname, phone, email, f"api/categories/{category}")

    return response.status_code


def check_password(email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    return auth_response.status_code


def instructors() -> List[Instructor]:
    data = cached_api_get(f"{api}instructors")
    if not data:
        return []

    return [
        Instructor(
            id=item['id'],
            name=item['name'],
            surname=item['surname'],
            patronymic=item.get('patronym', ''),
            phone=item['phone'],
            email=item['email'],
            dateOfBirth=item['dateOfBirth'],
            license=item['license'],
            hireDate=item['hireDate'],
            roles=item['roles'],
            image=item.get('image', 'static/img/default.png')
        ) for item in data
    ]


def get_instructor_by_id(id: int) -> Optional[Instructor]:
    data = cached_api_get(f"{api}users/{id}")
    if not data:
        return None

    return Instructor(
        id=data['id'],
        name=data['name'],
        surname=data['surname'],
        patronymic=data.get('patronym', ''),
        phone=data['phone'],
        email=data['email'],
        dateOfBirth=data['dateOfBirth'],
        license=data['license'],
        hireDate=data['hireDate'],
        roles=data['roles'],
        image=data.get('image', 'static/img/default.png')
    )


def teachers() -> List[Teacher]:
    data = cached_api_get(f"{api}teachers")
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
            image=item.get('image', 'static/img/default.png')
        ) for item in data
    ]


def get_teacher_by_id(id: int) -> Optional[Teacher]:
    data = cached_api_get(f"{api}teachers/{id}")
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
        image=data.get('image', 'static/img/default.png')
    )


def cars() -> List[Car]:
    data = cached_api_get(f"{api}cars")
    if not data:
        return []

    return [
        Car(
            id=item['id'],
            carMark=item['carMark']['title'],
            carModel=item['carModel'],
            stateNumber=item['stateNumber'],
            productionYear=item['productionYear'],
            vinNumber=item['vinNumber']
        ) for item in data
    ]


def get_car_by_id(id: int) -> Optional[Car]:
    data = cached_api_get(f"{api}cars/{id}")
    if not data:
        return None

    return Car(
        id=data['id'],
        carMark=data['carMark']['title'],
        carModel=data['carModel'],
        stateNumber=data['stateNumber'],
        productionYear=data['productionYear'],
        vinNumber=data['vinNumber']
    )


def categories():
    data = cached_api_get(f"{api}categories")
    if not data:
        return []

    return [
        Category(
            id=item['id'],
            title=item['title'],
            description=item['description']
        ) for item in data
    ]


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


def get_lesson_by_id(id: int) -> Optional[Lesson]:
    data = cached_api_get(f"{api}teacher_lessons/{id}")
    if not data:
        return None

    return Lesson(
        id=data['id'],
        title=data['title'],
        description=data['description'],
        lesson_type=data['type'],
        date=data['date']
    )


def start(id: int) -> Union[Student, Admin, Teacher, Instructor, int]:
    cached_api_get.cache_clear()
    data = cached_api_get(f"{api}users")
    if not data:
        return 0

    for user in data:
        if not isinstance(user, dict):
            continue

        if 'telegramId' not in user or user.get('telegramId') != str(id):
            continue

        if 'roles' not in user or not isinstance(user['roles'], list):
            continue

        if "ROLE_STUDENT" in user['roles']:
            user_obj = Student(
                id=user.get('id'),
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                contract=user.get('contract', ''),
                dateOfBirth=user.get('dateOfBirth'),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.png')
            )
            UserStorage.set_user(id, user_obj)
            return user_obj
        elif "ROLE_ADMIN" in user['roles']:
            user_obj = Admin(
                email=user.get('email', ''),
                username=user.get('username', '')
            )
            UserStorage.set_user(id, user_obj)
            return user_obj
        elif "ROLE_TEACHER" in user['roles']:
            user_obj = Teacher(
                id=user.get('id'),
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                dateOfBirth=user.get('dateOfBirth'),
                hireDate=user.get('hireDate'),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.png')
            )
            UserStorage.set_user(id, user_obj)
            return user_obj
        elif "ROLE_INSTRUCTOR" in user['roles']:
            user_obj = Instructor(
                id=user.get('id'),
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                dateOfBirth=user.get('dateOfBirth'),
                license=user.get('license', ''),
                hireDate=user.get('hireDate'),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.png')
            )
            UserStorage.set_user(id, user_obj)
            return user_obj
    return 0


def student_courses(id: int) -> List[Course]:
    data = cached_api_get(f"{api}students/{id}")
    if not data:
        return []

    list_courses = []
    if isinstance(data, dict) and 'courses' in data and isinstance(data['courses'], list):
        list_courses.extend([
            Course(
                id=c['id'],
                title=c['title'],
                description=c.get('description', ''),
                lessons=c.get('lessons', [])
            ) for c in data['courses'] if isinstance(c, dict)
        ])
    return list_courses


def update_user_data(id: int, surname: str, name: str, patronymic: str, password: str) -> int:
    user_data = cached_api_get(f"{api}users/{id}")

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
                "patronymic": patronymic
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


def drive_schedules() -> List[Schedule]:
    data = cached_api_get(f"{api}drive_schedules")
    if not data:
        return []

    return [
        Schedule(
            id=item.get('id', 0),
            time_from=item.get('timeFrom', 'Не указано'),
            time_to=item.get('timeTo', 'Не указано'),
            days_of_week=item.get('daysOfWeek', []),
            notice=item.get('notice', ''),
            autodrome_id=item.get('autodrome', {}).get('id'),
            category_id=item.get('category', {}).get('id'),
            instructor_id=item.get('instructor', {}).get('id')
        ) for item in data
    ]


def get_drive_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
    data = cached_api_get(f"{api}drive_schedules/{schedule_id}")

    if not data:
        return None

    return Schedule(
        id=data.get('id', 0),
        time_from=data.get('timeFrom', 'Не указано'),
        time_to=data.get('timeTo', 'Не указано'),
        days_of_week=data.get('daysOfWeek', []),
        notice=data.get('notice', ''),
        autodrome_id=data.get('autodrome', {}).get('id'),
        category_id=data.get('category', {}).get('id'),
        instructor_id=data.get('instructor', {}).get('id')
    )


def get_autodrome_by_id(id: int) -> Autodrome:
    data = cached_api_get(f"{api}autodromes/{id}")

    if not data:
        return Autodrome(
            id=id,
            title="Не удалось загрузить",
            address="Не удалось загрузить",
            description="Не удалось загрузить"
        )

    return Autodrome(
        id=data['id'],
        title=data.get('title', 'Не указано'),
        address=data.get('address', 'Не указан'),
        description=data.get('description', 'Не указано')
    )


def get_category_by_id(id: int) -> Category:
    data = cached_api_get(f"{api}categories/{id}")

    if not data:
        return Category(
            id=id,
            title="Не удалось загрузить",
            description="Не удалось загрузить"
        )

    return Category(
        id=data['id'],
        title=data.get('title', 'Не указано'),
        description=data.get('description', 'Не указано')
    )


def post_instructor_lesson(user_id: int, instructor_id: int, autodrome_id: int,
                           category_id: int, date_time: str, password: str) -> int:
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
