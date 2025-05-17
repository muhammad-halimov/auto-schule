from dataclasses import dataclass
from typing import Optional, List

from app.utils.api_helpers import cached_api_get
from config_local import api


@dataclass
class Car:
    id: int
    carMark: str
    carModel: str
    stateNumber: str
    productionYear: str
    vinNumber: str


def cars() -> List[Car]:
    data = cached_api_get(f"{api}cars")
    if not data:
        return []

    return [
        Car(
            id=item['id'],
            carMark=item['carMark']['title'],
            carModel=item['carModel'],
            stateNumber=item['stateNumber'],
            productionYear=item['productionYear'],
            vinNumber=item['vinNumber']
        ) for item in data
    ]


def get_car_by_id(car_id: int) -> Optional[Car]:
    data = cached_api_get(f"{api}cars/{car_id}")
    if not data:
        return None

    return Car(
        id=data['id'],
        carMark=data['carMark']['title'],
        carModel=data['carModel'],
        stateNumber=data['stateNumber'],
        productionYear=data['productionYear'],
        vinNumber=data['vinNumber']
    )
