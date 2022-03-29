import boto3
from decouple import config
from fastapi import HTTPException


class S3Service:
    def __init__(self):
        self.key = config("AWS_ACCESS_KEY")
        self.secret = config("AWS_SECRET_KEY")
        self.s3 = boto3.client(
            "s3", aws_access_key_id=self.key, aws_secret_access_key=self.secret
        )
        self.bucket = config("AWS_BUCKET_PHOTO")
        self.region = config("AWS_REGION")

    def upload_photo(self, path, photo_key, photo_ext):
        try:
            self.s3.upload_file(
                path,
                self.bucket,
                photo_key,
                ExtraArgs={"ACL": "public-read", "ContentType": f"image/{photo_ext}"},
            )
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{photo_key}"
        except Exception as ex:
            raise HTTPException(500, "S3 is not available")
