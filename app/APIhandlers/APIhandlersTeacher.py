from dataclasses import dataclass
from typing import List, Optional

from app.utils.api_helpers import cached_api_get
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
    data = cached_api_get(f"{api}users/{id}")
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
