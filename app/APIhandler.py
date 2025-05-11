import json
import logging
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
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


def cached_api_get_with_headers(url: str, headers: dict):
    try:
        # Явно указываем параметры метода get
        response = requests.get(
            url=url,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
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
    type: str


@dataclass
class Admin:
    id: int
    email: str
    username: str
    type: str


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
    type: str


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
    type: str


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
class DriveLesson:
    id: int
    instructor: Dict
    student: Dict
    date: str
    autodrome: Dict
    category: Dict


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


@dataclass
class UserCredentials:
    user: Union[Student, Admin, Teacher, Instructor]
    password: str
    telegram_id: int
    db_id: int

    def to_dict(self):
        user_dict = self.user.__dict__.copy()
        if 'password' in user_dict:
            del user_dict['password']
        return {
            'user_data': user_dict,
            'password': self.password,
            'telegram_id': self.telegram_id,
            'db_id': self.db_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        user_type = data['user_data'].get('type')
        user_class = {
            'student': Student,
            'admin': Admin,
            'teacher': Teacher,
            'instructor': Instructor
        }.get(user_type)

        user_data = data['user_data'].copy()
        if 'password' in user_data:
            del user_data['password']

        user = user_class(**user_data)
        return cls(
            user=user,
            password=data['password'],
            telegram_id=data['telegram_id'],
            db_id=data['db_id']
        )


class UserStorage:
    _instance = None
    _users: Dict[int, UserCredentials] = {}  # Ключ - telegram_id
    _storage_dir = Path('jsons')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._storage_dir.mkdir(exist_ok=True)
        return cls._instance

    def _get_user_file(self, telegram_id: int) -> Path:
        return self._storage_dir / f'user_tg_{telegram_id}_data.json'

    def _load_user(self, telegram_id: int):
        user_file = self._get_user_file(telegram_id)

        if not user_file.exists():
            return None

        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return UserCredentials.from_dict(data)
        except Exception as e:
            print(f"Error loading user {telegram_id} data: {e}")
            return None

    def _save_user(self, telegram_id: int, credentials: UserCredentials):
        user_file = self._get_user_file(telegram_id)
        try:
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(credentials.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving user {telegram_id} data: {e}")

    def _delete_user_file(self, user_id: int):
        user_file = self._get_user_file(user_id)
        try:
            if user_file.exists():
                os.remove(user_file)
        except Exception as e:
            print(f"Error deleting user {user_id} file: {e}")

    def get_user(self, telegram_id: int) -> Optional[Union[Student, Admin, Teacher, Instructor]]:
        if telegram_id in self._users:
            return self._users[telegram_id].user

        credentials = self._load_user(telegram_id)
        if credentials:
            self._users[telegram_id] = credentials
            return credentials.user

        return None

    def get_user_by_db_id(self, db_id: int) -> Optional[Union[Student, Admin, Teacher, Instructor]]:
        # Сначала проверяем кэш
        for creds in self._users.values():
            if creds.db_id == db_id:
                return creds.user

        # Ищем в файлах
        for file in self._storage_dir.glob('user_*_data.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('db_id') == db_id:
                        credentials = UserCredentials.from_dict(data)
                        self._users[credentials.telegram_id] = credentials
                        return credentials.user
            except (json.JSONDecodeError, OSError):
                # Catch specific file and JSON parsing errors
                continue
        return None

    def get_credentials(self, user_id: int) -> Optional[UserCredentials]:
        if user_id not in self._users:
            credentials = self._load_user(user_id)
            if credentials:
                self._users[user_id] = credentials
        return self._users.get(user_id)

    def set_user(self, telegram_id: int, db_id: int,
                 user_data: Union[Student, Admin, Teacher, Instructor],
                 password: str = ''):
        credentials = UserCredentials(
            user=user_data,
            password=password,
            telegram_id=telegram_id,
            db_id=db_id
        )
        self._users[telegram_id] = credentials
        self._save_user(telegram_id, credentials)

    def set_password(self, user_id: int, password: str, db_id: int = None):
        if user_id not in self._users:
            if db_id is None:
                raise ValueError("Для нового пользователя требуется db_id")

            self.set_user(
                telegram_id=user_id,
                user_data=Student(
                    id=user_id,
                    name="",
                    surname="",
                    patronymic="",
                    phone="",
                    email="",
                    contract="",
                    dateOfBirth="",
                    roles=[],
                    image="static/img/default.jpg",
                    type="student"),
                password=password,
                db_id=db_id
            )
        else:
            self._users[user_id].password = password
            self._save_user(user_id, self._users[user_id])

    def verify_password(self, user_id: int, password: str) -> bool:
        credentials = self.get_credentials(user_id)
        return credentials and credentials.password == password

    def clear_user(self, user_id: int):
        if user_id in self._users:
            del self._users[user_id]
        self._delete_user_file(user_id)

    def get_all_users(self) -> Dict[int, UserCredentials]:
        user_files = self._storage_dir.glob('user*_data.json')
        for file in user_files:
            try:
                user_id = int(file.stem[4:-5])
                if user_id not in self._users:
                    self._users[user_id] = self._load_user(user_id)
            except ValueError:
                continue
        return self._users.copy()


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
            image=item.get('image', 'static/img/default.jpg'),
            type='instructor') for item in data
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
        image=data.get('image', 'static/img/default.jpg'),
        type='instructor'
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
            image=item.get('image', 'static/img/default.jpg'),
            type='teacher'
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
        image=data.get('image', 'static/img/default.jpg'),
        type='teacher'
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


def start(telegram_id: int) -> Union[Student, Admin, Teacher, Instructor, int]:
    cached_api_get.cache_clear()
    data = cached_api_get(f"{api}users")
    if not data:
        return 0

    for user in data:
        if not isinstance(user, dict):
            continue

        if 'telegramId' not in user or user.get('telegramId') != str(telegram_id):
            continue

        if 'roles' not in user or not isinstance(user['roles'], list):
            continue

        db_id = user.get('id')
        if not db_id:
            continue

        storage = UserStorage()

        if "ROLE_STUDENT" in user['roles']:
            user_obj = Student(
                id=db_id,
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                contract=user.get('contract', ''),
                dateOfBirth=user.get('dateOfBirth', ''),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.jpg'),
                type='student'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
            return user_obj
        elif "ROLE_ADMIN" in user['roles']:
            user_obj = Admin(
                id=db_id,
                email=user.get('email', ''),
                username=user.get('username', ''),
                type='admin'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
            return user_obj
        elif "ROLE_TEACHER" in user['roles']:
            user_obj = Teacher(
                id=db_id,
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                dateOfBirth=user.get('dateOfBirth'),
                hireDate=user.get('hireDate'),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.jpg'),
                type='teacher'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
            return user_obj
        elif "ROLE_INSTRUCTOR" in user['roles']:
            user_obj = Instructor(
                id=db_id,
                name=user.get('name', ''),
                surname=user.get('surname', ''),
                patronymic=user.get('patronym', ''),
                phone=user.get('phone', ''),
                email=user.get('email', ''),
                dateOfBirth=user.get('dateOfBirth'),
                license=user.get('license', ''),
                hireDate=user.get('hireDate'),
                roles=user['roles'],
                image=user.get('image', 'static/img/default.jpg'),
                type='instructor'
            )
            storage.set_user(
                telegram_id=telegram_id,
                db_id=db_id,
                user_data=user_obj,
                password="default_password"
            )
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


def my_schedules(student_id: int, email: str, password: str) -> list[DriveLesson] | int:
    try:
        # Получаем токен аутентификации
        auth_response = requests.post(
            f"{api}authentication_token",
            json={"email": email, "password": password}
        )

        # Проверяем успешность запроса
        if auth_response.status_code != 200:
            print(f"Authentication failed: {auth_response.status_code}")
            return 0

        auth_data = auth_response.json()
        token = auth_data.get('token')
        if not token:
            print("No token in auth response")
            return 0

        # Формируем заголовки
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Делаем запрос с правильными заголовками
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

            # Обработка даты и создание объекта DriveLesson
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
                student={
                    'id': item.get('student', {}).get('id', 0),
                    'name': item.get('student', {}).get('name', ''),
                    'surname': item.get('student', {}).get('surname', '')
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


def find_user_by_telegram_id(telegram_id: int) -> Optional[int]:
    users_data = cached_api_get(f"{api}users")
    if not users_data:
        return 0

    for user in users_data:
        if not isinstance(user, dict):
            continue

        if 'telegramId' in user and user.get('telegramId') == str(telegram_id):
            db_id = user.get('id')
            print(db_id, "API")
            if db_id is None:
                return 0
            else:
                return db_id
