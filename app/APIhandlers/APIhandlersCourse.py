from dataclasses import dataclass
from typing import List, Dict, Optional

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Course:
    id: int
    title: str
    description: str
    lessons: List[Dict]


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
