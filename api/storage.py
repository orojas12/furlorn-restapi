import mimetypes
import os
from uuid import uuid4

from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


aws = Session(
    aws_access_key_id=settings.S3_STORAGE["AWS_ACCESS_KEY"],
    aws_secret_access_key=settings.S3_STORAGE["AWS_SECRET_ACCESS_KEY"],
    region_name=settings.S3_STORAGE["AWS_REGION"],
)
bucket = aws.resource("s3").Bucket(settings.S3_STORAGE["BUCKET_NAME"])
client = aws.client("s3", config=Config(signature_version="s3v4"))


@deconstructible
class S3Storage(Storage):
    def _open(self):
        ...

    def _save(self, name, content):
        content_type, encoding = mimetypes.guess_type(name)
        try:
            bucket.put_object(Body=content.read(), ContentType=content_type, Key=name)
            content.close()
        except ClientError as e:
            raise e
        return name

    def delete(self, name):
        try:
            bucket.Object(name).delete()
        except ClientError as e:
            raise e

    def exists(self, name):
        try:
            # verify if object with name exists in bucket
            response = bucket.Object(name).load()
        except ClientError as e:
            if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
                return False
            else:
                # Something else went wrong.
                raise e
        else:
            return response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def size(self, name):
        ...

    def url(self, name):
        try:
            url = client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": settings.S3_STORAGE["BUCKET_NAME"], "Key": name},
                ExpiresIn=60,
            )
            return url
        except ClientError as e:
            return None

    def get_available_name(self, name, max_length=None):
        filename = self.get_unique_name(name)
        if self.exists(filename):
            # Generate new name until it's unique.
            return self.get_available_name(name)
        return filename

    def get_unique_name(self, name):
        _, ext = os.path.splitext(name)
        return str(uuid4()) + ext
