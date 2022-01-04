import logging
from uuid import uuid4

from boto3 import resource
from botocore.exceptions import ClientError
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import CharField, UUIDField
from django.db.models.fields.related import ForeignKey

bucket_id = "neighborhoodlostpets.com"
s3 = resource("s3")
logger = logging.getLogger(__name__)


class Sex(models.IntegerChoices):
    # These values are based on the ISO/IEC 5218 standard.
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NOT_APPLICABLE = 9


class Animal(models.TextChoices):
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


class Breed(models.Model):
    name = models.CharField(max_length=50)
    animal = models.CharField(max_length=50, choices=Animal.choices)


class Pet(models.Model):
    class Color(models.TextChoices):
        WHITE = "white"
        BLACK = "black"
        BROWN = "brown"
        ORANGE = "orange"
        RED = "red"
        PINK = "pink"
        PURPLE = "purple"
        BLUE = "blue"
        GREEN = "green"
        YELLOW = "yellow"
        GRAY = "gray"

    class Status(models.TextChoices):
        LOST = "lost"
        FOUND = "found"
        REUNITED = "reunited"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    animal = models.CharField(max_length=50, choices=Animal.choices)
    breed = models.ManyToManyField("Breed", blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    sex = models.IntegerField(choices=Sex.choices, blank=True, default=Sex.UNKNOWN)
    eye_color = models.CharField(
        max_length=50, choices=Color.choices, blank=True, default=""
    )
    color = models.CharField(
        max_length=50, choices=Color.choices, blank=True, default=""
    )
    weight = models.PositiveIntegerField(blank=True, null=True)
    microchip = models.CharField(max_length=15, blank=True, default="")
    information = models.CharField(max_length=5000, blank=True, default="")
    status = models.CharField(max_length=50, choices=Status.choices)

    user = models.ForeignKey(User, related_name="pets", on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)


class Photo(models.Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    url = CharField(max_length=200)
    pet = ForeignKey("Pet", related_name="photos", on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        self.file_stream = kwargs.pop("file_stream", None)
        self.content_type = kwargs.pop("content_type", None)
        super().__init__(*args, **kwargs)

    def put_s3_object(self):
        s3_obj = s3.Object(bucket_id, str(self.id))

        return s3_obj.put(
            Body=self.file_stream,
            ContentType=self.content_type,
        )

    def save(self, *args, **kwargs):
        try:
            response = self.put_s3_object()
        except ClientError as e:
            logger.warning(e)  # log this error
            raise self.SaveError("Failed to save object to s3") from e
        logger.info(response)  # log
        super().save(*args, **kwargs)

    class SaveError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(message)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey("Pet", on_delete=models.CASCADE)
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    text = models.CharField(max_length=2000)
