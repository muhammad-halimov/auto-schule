from dataclasses import dataclass

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Autodrome:
    id: int
    title: str
    address: str
    description: str


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
