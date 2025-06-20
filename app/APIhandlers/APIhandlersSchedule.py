from dataclasses import dataclass
from typing import List, Optional

import requests

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
    data = requests.get(f"{api}drive_schedules").json()
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


def admin_drive_schedules() -> List[Schedule]:
    data = requests.get(f"{api}drive_schedules").json()
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
    data = requests.get(f"{api}drive_schedules/{schedule_id}").json()

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


def get_admin_drive_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
    data = requests.get(f"{api}drive_schedules/{schedule_id}").json()

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


def delete_schedule_from_api(schedule_id, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    result = requests.delete(url=f"{api}drive_schedules/{schedule_id}", headers=headers)
    return result.status_code


def update_schedule(schedule_id, json, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/merge-patch+json"
    }

    result = requests.patch(url=f"{api}drive_schedules/{schedule_id}", headers=headers, json=json)
    print(result.text)
    return result.status_code


def add_schedule(schedule_data, email, password):
    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": email, "password": password}
    )

    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return None

    auth_data = auth_response.json()
    token = auth_data.get('token')
    if not token:
        print("No token in auth response")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    result = requests.post(url=f"{api}drive_schedules", headers=headers, json=schedule_data)
    return result.status_code


def instructor_drive_schedule(user_id):
    data = requests.get(f"{api}drive_schedules").json()
    if not data:
        return 0

    res = Schedule

    print(data, user_id)

    for schedule in data:
        if schedule.get('instructor', {}).get('id') == user_id:
            res = Schedule(
                id=schedule.get('id', 0),
                time_from=schedule.get('timeFrom', 'Не указано'),
                time_to=schedule.get('timeTo', 'Не указано'),
                days_of_week=schedule.get('daysOfWeek', []),
                notice=schedule.get('notice', ''),
                autodrome_id=schedule.get('autodrome', {}).get('id'),
                category_id=schedule.get('category', {}).get('id'),
                instructor_id=schedule.get('instructor', {}).get('id'))
        else:
            return 0

    return res
