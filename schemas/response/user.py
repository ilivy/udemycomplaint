from models import RoleType
from schemas.base import BaseUser


class UserOut(BaseUser):
    id: str
    first_name: str
    last_name: str
    phone: str
    iban: str
    role: RoleType
