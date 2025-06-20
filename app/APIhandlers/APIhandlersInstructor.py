from dataclasses import dataclass
from typing import List, Optional

import requests

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
    data = requests.get(f"{api}instructors").json()
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


def admin_instructors() -> List[Instructor]:
    data = requests.get(f"{api}instructors").json()
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


def get_instructor_by_id(instructor_id: int) -> Optional[Instructor]:
    data = requests.get(f"{api}users/{instructor_id}").json()
    if not data:
        return None
    print(instructor_id)

    return Instructor(
        id=instructor_id,
        name=data.get('name'),
        surname=data.get('surname'),
        patronymic=data.get('patronym', ''),
        phone=data.get('phone'),
        email=data.get('email'),
        dateOfBirth=data.get('dateOfBirth'),
        license=data.get('license'),
        experience=data.get('experience'),
        hireDate=data.get('hireDate'),
        roles=data.get('roles'),
        image=data.get('image', 'static/img/default.jpg'),
        type='instructor'
    )
