from dataclasses import dataclass
from typing import List, Optional

from app.utils.api_helpers import cached_api_get
from config_local import api


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
    experience: int
    hireDate: str
    roles: List[str]
    image: str
    type: str


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
            experience=item['experience'],
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
        experience=data['experience'],
        hireDate=data['hireDate'],
        roles=data['roles'],
        image=data.get('image', 'static/img/default.jpg'),
        type='instructor'
    )
