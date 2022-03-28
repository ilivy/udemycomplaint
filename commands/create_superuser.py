import asyncclick as aclick

from db import database
from managers.user import UserManager
from models import RoleType


@aclick.command()
@aclick.option("-f", "--first_name", type=str, required=True)
@aclick.option("-l", "--last_name", type=str, required=True)
@aclick.option("-e", "--email", type=str, required=True)
@aclick.option("-p", "--password", type=str, required=True)
@aclick.option("-ph", "--phone", type=str, required=True)
@aclick.option("-i", "--iban", type=str, required=True)
async def create_admin(first_name, last_name, email, password, phone, iban):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "phone": phone,
        "iban": iban,
        "role": RoleType.admin,
    }
    await database.connect()
    await UserManager.register(user_data)
    await database.disconnect()


if __name__ == "__main__":
    create_admin(_anyio_backend="asyncio")
