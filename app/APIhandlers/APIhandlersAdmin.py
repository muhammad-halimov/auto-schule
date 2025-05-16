from dataclasses import dataclass


@dataclass
class Admin:
    id: int
    email: str
    username: str
    type: str
