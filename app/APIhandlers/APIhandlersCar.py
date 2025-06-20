from dataclasses import dataclass
from typing import Optional, List, Dict

import requests

from config_local import api


@dataclass
class Car:
    id: int
    carMark: Dict
    carModel: str
    stateNumber: str
    productionYear: str
    vinNumber: str


def cars() -> List[Car]:
    data = requests.get(f"{api}cars").json()
    if not data:
        return []

    return [
        Car(
            id=item['id'],
            carMark=item.get('carMark', {}).get('title', ''),
            carModel=item.get('carModel', ''),
            stateNumber=item.get('stateNumber', ''),
            productionYear=item.get('productionYear', ''),
            vinNumber=item.get('vinNumber', '')
        ) for item in data
    ]


def admin_cars() -> List[Car]:
    data = requests.get(f"{api}cars").json()
    if not data:
        return []

    return [
        Car(
            id=item['id'],
            carMark=item.get('carMark', {}).get('title', ''),
            carModel=item.get('carModel', ''),
            stateNumber=item.get('stateNumber', ''),
            productionYear=item.get('productionYear', ''),
            vinNumber=item.get('vinNumber', '')
        ) for item in data
    ]


def get_car_by_id(car_id: int) -> Optional[Car]:
    data = requests.get(f"{api}cars/{car_id}").json()
    if not data:
        return None

    return Car(
        id=data['id'],
        carMark=data.get('carMark', {}).get('title', ''),
        carModel=data.get('carModel', ''),
        stateNumber=data.get('stateNumber', ''),
        productionYear=data.get('productionYear', ''),
        vinNumber=data.get('vinNumber', '')
    )


def get_admin_car_by_id(car_id: int) -> Optional[Car]:
    data = requests.get(f"{api}cars/{car_id}").json()
    if not data:
        return None

    return Car(
        id=car_id,
        carMark=data.get('carMark', {}),
        carModel=data.get('carModel', ''),
        stateNumber=data.get('stateNumber', ''),
        productionYear=data.get('productionYear', ''),
        vinNumber=data.get('vinNumber', '')
    )


def delete_car(car_id, email, password):
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
        "Authorization": f"Bearer {token}"
    }

    result = requests.delete(url=f"{api}cars/{car_id}", headers=headers)
    print(result.status_code, result.text)
    return result.status_code


def update_car_in_api(car_id, car_data, email, password):
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

    result = requests.patch(url=f"{api}cars/{car_id}", headers=headers, json=car_data)
    return result.status_code


def add_car_to_api(car_data, email, password):
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

    result = requests.post(url=f"{api}cars", headers=headers, json=car_data)
    print(result.status_code, result.text)
    return result.status_code


def get_car_mark_title(mark_id):
    marks = get_all_marks_car()
    for mark in marks:
        if mark.get('id') == mark_id:
            return mark.get("title")
    return "Не указана"


def get_all_marks_car():
    auto_producers = requests.get(f"{api}auto_producers").json()
    marks_list = []

    for auto_producer in auto_producers:
        marks_list.append(auto_producer)

    return marks_list
