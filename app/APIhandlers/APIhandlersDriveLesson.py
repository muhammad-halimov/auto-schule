from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

import requests

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class DriveLesson:
    id: int
    instructor: Dict
    date: str
    autodrome: Dict
    category: Dict


def post_instructor_lesson(user_id: int, instructor_id: int, autodrome_id: int,
                           category_id: int, date_time: str, password: str) -> int:
    users = cached_api_get(f"{api}users")
    if not users:
        return 0

    user_data = next((u for u in users if 'telegramId' in u and u['telegramId'] == str(user_id)), None)
    if not user_data:
        return 0

    auth_response = requests.post(
        f"{api}authentication_token",
        json={"email": user_data['email'], "password": password}
    )

    token = auth_response.json().get('token')
    if not token:
        return 0

    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    dt_utc = dt.replace(tzinfo=timezone.utc)
    iso_format = dt_utc.isoformat(timespec='milliseconds')

    response = requests.post(
        f"{api}instructor_lessons",
        json={
            "instructor": f"/api/users/{instructor_id}",
            "student": f"/api/users/{user_data['id']}",
            "date": f"{iso_format}",
            "autodrome": f"/api/autodromes/{autodrome_id}",
            "category": f"/api/categories/{category_id}"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    return response.status_code
