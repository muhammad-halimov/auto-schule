import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Dict, Optional

import requests

from app.APIhandlers.APIhandlersAdmin import Admin
from app.APIhandlers.APIhandlersInstructor import Instructor
from app.APIhandlers.APIhandlersStudent import Student
from app.APIhandlers.APIhandlersTeacher import Teacher
from app.utils.api_helpers import cached_api_get
from config_local import api


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
    _users: Dict[int, UserCredentials] = {}
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
        for creds in self._users.values():
            if creds.db_id == db_id:
                return creds.user

        for file in self._storage_dir.glob('user_*_data.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('db_id') == db_id:
                        credentials = UserCredentials.from_dict(data)
                        self._users[credentials.telegram_id] = credentials
                        return credentials.user
            except (json.JSONDecodeError, OSError):
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

    def update_user_from_api(self, telegram_id: int) -> bool:
        credentials = self.get_credentials(telegram_id)
        if not credentials:
            return False

        api_url = f"{api}users/{credentials.db_id}"
        data = requests.get(api_url).json()

        if not data:
            return False

        field_mapping = {
            'patronym': 'patronymic',
        }

        default_values = {
            "contract": "11111111111",
            "dateOfBirth": "",
            'image': 'static/img/default.jpg',
            'type': 'student'
        }

        filtered_data = {}
        for k, v in data.items():
            mapped_key = field_mapping.get(k, k)
            if mapped_key in {
                'id', 'name', 'surname', 'patronymic', 'phone', 'email',
                'roles', 'image', 'type'
            }:
                filtered_data[mapped_key] = v

        for field, default_value in default_values.items():
            if field not in filtered_data:
                filtered_data[field] = default_value

        required_fields = {
            'id', 'name', 'surname', 'patronymic', 'phone', 'email',
            'roles', 'image', 'type'
        }
        if not required_fields.issubset(filtered_data.keys()):
            print(f"Missing required fields: {required_fields - set(filtered_data.keys())}")
            return False

        original_password = credentials.password
        original_telegram_id = credentials.telegram_id
        original_db_id = credentials.db_id

        user_classes = {
            'student': Student,
            'admin': Admin,
            'teacher': Teacher,
            'instructor': Instructor
        }

        user_class = user_classes.get(filtered_data.get('type'))
        if not user_class:
            return False

        try:
            updated_user = user_class(**filtered_data)

            self.set_user(
                telegram_id=original_telegram_id,
                db_id=original_db_id,
                user_data=updated_user,
                password=original_password
            )
            return True
        except Exception as e:
            print(f"Error updating user from API: {e}")
            return False
