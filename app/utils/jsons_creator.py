import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import requests

from config_local import api


@dataclass
class UserCredentials:
    email: str
    password: str
    telegram_id: int
    db_id: int

    def to_dict(self):
        return {
            'email': self.email,
            'password': self.password,
            'telegram_id': self.telegram_id,
            'db_id': self.db_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            email=data['email'],
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

    def _load_user(self, telegram_id: int) -> Optional[UserCredentials]:
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

    def get_user_credentials(self, telegram_id: int) -> Optional[UserCredentials]:
        if telegram_id in self._users:
            return self._users[telegram_id]

        credentials = self._load_user(telegram_id)
        if credentials:
            self._users[telegram_id] = credentials
            return credentials

        return None

    def get_user_by_db_id(self, db_id: int) -> Optional[UserCredentials]:
        for creds in self._users.values():
            if creds.db_id == db_id:
                return creds

        for file in self._storage_dir.glob('user_*_data.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('db_id') == db_id:
                        credentials = UserCredentials.from_dict(data)
                        self._users[credentials.telegram_id] = credentials
                        return credentials
            except (json.JSONDecodeError, OSError):
                continue
        return None

    def set_user(self, telegram_id: int, db_id: int, email: str, password: str = ''):
        credentials = UserCredentials(
            email=email,
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
                db_id=db_id,
                email="",
                password=password
            )
        else:
            self._users[user_id].password = password
            self._save_user(user_id, self._users[user_id])

    def verify_password(self, user_id: int, password: str) -> bool:
        credentials = self.get_user_credentials(user_id)
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
        credentials = self.get_user_credentials(telegram_id)
        if not credentials:
            return False

        api_url = f"{api}users/{credentials.db_id}"
        response = requests.get(api_url)

        if not response.ok:
            return False

        try:
            data = response.json()
            email = data.get('email', credentials.email)

            self.set_user(
                telegram_id=telegram_id,
                db_id=credentials.db_id,
                email=email,
                password=credentials.password
            )
            return True
        except Exception as e:
            print(f"Error updating user from API: {e}")
            return False