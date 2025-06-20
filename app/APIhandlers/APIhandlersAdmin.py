from dataclasses import dataclass
from typing import List


@dataclass
class Admin:
    id: int
    email: str
    name: str
    surname: str
    patronymic: str
    phone: str
    contract: str
    dateOfBirth: str
    roles: List
    image: str
    type: str
