from dataclasses import dataclass
from typing import Optional, List, Dict

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Lesson:
    id: int
    title: str
    description: str
    lesson_type: str
    date: str
    videos: List[Dict]


def get_lesson_by_id(id: int) -> Optional[Lesson]:
    data = cached_api_get(f"{api}teacher_lessons/{id}")
    if not data:
        return None

    return Lesson(
        id=data['id'],
        title=data['title'],
        description=data['description'],
        lesson_type=data['type'],
        date=data['date'],
        videos=data['videos']
    )
