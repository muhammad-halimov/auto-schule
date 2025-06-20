from dataclasses import dataclass

import requests

from config_local import api


@dataclass
class Autodrome:
    id: int
    title: str
    address: str
    description: str


def autodromes():
    data = requests.get(f"{api}autodromes").json()

    if not data:
        return None

    return [
        Autodrome(
            id=item['id'],
            title=item.get('title', 'Не указано'),
            address=item.get('address', 'Не указан'),
            description=item.get('description', 'Не указано')
        )for item in data
    ]


def get_autodrome_by_id(autodrome_id: int) -> Autodrome:
    data = requests.get(f"{api}autodromes/{autodrome_id}").json()

    if not data:
        return Autodrome(
            id=autodrome_id,
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
