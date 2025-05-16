from dataclasses import dataclass
from typing import List, Optional

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Schedule:
    id: int
    time_from: str
    time_to: str
    days_of_week: List[str]
    notice: str
    autodrome_id: Optional[int]
    category_id: Optional[int]
    instructor_id: Optional[int]


def drive_schedules() -> List[Schedule]:
    data = cached_api_get(f"{api}drive_schedules")
    if not data:
        return []

    return [
        Schedule(
            id=item.get('id', 0),
            time_from=item.get('timeFrom', 'Не указано'),
            time_to=item.get('timeTo', 'Не указано'),
            days_of_week=item.get('daysOfWeek', []),
            notice=item.get('notice', ''),
            autodrome_id=item.get('autodrome', {}).get('id'),
            category_id=item.get('category', {}).get('id'),
            instructor_id=item.get('instructor', {}).get('id')
        ) for item in data
    ]


def get_drive_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
    data = cached_api_get(f"{api}drive_schedules/{schedule_id}")

    if not data:
        return None

    return Schedule(
        id=data.get('id', 0),
        time_from=data.get('timeFrom', 'Не указано'),
        time_to=data.get('timeTo', 'Не указано'),
        days_of_week=data.get('daysOfWeek', []),
        notice=data.get('notice', ''),
        autodrome_id=data.get('autodrome', {}).get('id'),
        category_id=data.get('category', {}).get('id'),
        instructor_id=data.get('instructor', {}).get('id')
    )
