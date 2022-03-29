import os
import uuid

from constants import TEMP_FILE_FOLDER
from db import database
from models import complaint, RoleType, State, transaction
from services.s3 import S3Service
from services.ses import SESService
from services.wise import WiseService
from utils.helpers import decode_photo

s3 = S3Service()
ses = SESService()
wise = WiseService()


class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        q = complaint.select()
        if user["role"] == RoleType.complainer:
            q = q.where(complaint.c.complainer_id == user["id"])
        elif user["role"] == RoleType.approver:
            q = q.where(complaint.c.state == State.pending)
        return await database.fetch_all(q)

    @staticmethod
    async def create_complaint(complaint_data, user):
        complaint_data["complainer_id"] = user["id"]
        encoded_photo = complaint_data.pop("encoded_photo")
        extension = complaint_data.pop("extension")
        # name = f"{uuid.uuid4()}.{extension}"
        # path = os.path.join(TEMP_FILE_FOLDER, name)
        # decode_photo(path, encoded_photo)
        # complaint_data["photo_url"] = s3.upload_photo(path, name, extension)
        complaint_data[
            "photo_url"
        ] = "https://upload.wikimedia.org/wikipedia/commons/6/6e/065-365-_Show_us_your_smile%21_%282765083201%29.jpg"
        # os.remove(path)

        # DB transaction is used here
        # in order to guarantee that both operations: user's complaint and money transaction
        # has been stored together, or none of them has been stored
        async with database.transaction() as tconn:
            id_ = await tconn._connection.execute(complaint.insert().values(complaint_data))
            await ComplaintManager.issue_transaction(
                tconn,
                complaint_data["amount"],
                f"{user['first_name']} {user['last_name']}",
                user["iban"],
                id_,
            )
        return await database.fetch_one(complaint.select().where(complaint.c.id == id_))

    @staticmethod
    async def delete(complaint_id):
        await database.execute(complaint.delete().where(complaint.c.id == complaint_id))

    @staticmethod
    async def approve(complaint_id):
        await database.execute(
            complaint.update()
            .where(complaint.c.id == complaint_id)
            .values(state=State.approved)
        )
        transaction_data = await database.fetch_one(
            transaction.select().where(transaction.c.complaint_id == complaint_id)
        )
        wise.fund_transfer(transaction_data["transfer_id"])
        # ses.send_mail(
        #     "Complaint approved!",
        #     ["we@d.com"],
        #     "Congrats! Your complaint has been approved, check your bank account in two days for your refund.",
        # )

    @staticmethod
    async def reject(complaint_id):
        transaction_data = await database.fetch_one(
            transaction.select().where(transaction.c.complaint_id == complaint_id)
        )
        wise.cancel_transfer(transaction_data["transfer_id"])
        await database.execute(
            complaint.update()
            .where(complaint.c.id == complaint_id)
            .values(state=State.rejected)
        )

    @staticmethod
    async def issue_transaction(tconn, amount, full_name, iban, complaint_id):
        """
        :param tconn: comes from create_complaint() method
        :param amount:
        :param full_name:
        :param iban:
        :param complaint_id:
        :return:
        """
        quote_id = wise.create_quote(amount)
        target_account_id = wise.create_recipient_account(full_name, iban)
        transfer_id = wise.create_transfer(target_account_id, quote_id)
        data = {
            "quote_id": quote_id,
            "transfer_id": transfer_id,
            "target_account_id": str(target_account_id),
            "amount": amount,
            "complaint_id": complaint_id,
        }
        await tconn._connection.execute(transaction.insert().values(**data))
