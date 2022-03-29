import boto3
from decouple import config
from fastapi import HTTPException


class SESService:
    def __init__(self):
        self.key = config("AWS_ACCESS_KEY")
        self.secret = config("AWS_SECRET_KEY")
        self.region = config("AWS_REGION")
        self.ses = boto3.client(
            "ses",
            region_name=self.region,
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
        )

    def send_mail(self, subject, to_addresses, text_data):
        subj = {"Data": subject, "Charset": "UTF-8"}
        body = {"Text": {"Data": text_data, "Charset": "UTF-8"}}

        self.ses.send_email(
            Source=config("EMAIL_FROM"),
            Destination={
                "ToAddresses": to_addresses,
                "CCAddresses": [],
                "BCCAddresses": [],
            },
            Message={"Subject": subj, "Body": body},
        )
