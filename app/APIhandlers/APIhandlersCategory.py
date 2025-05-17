from dataclasses import dataclass

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Category:
    id: int
    title: str
    description: str


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


def get_category_by_id(category_id: int) -> Category:
    data = cached_api_get(f"{api}categories/{category_id}")

    if not data:
        return Category(
            id=category_id,
            title="Не удалось загрузить",
            description="Не удалось загрузить"
        )

    return Category(
        id=data['id'],
        title=data.get('title', 'Не указано'),
        description=data.get('description', 'Не указано')
    )
