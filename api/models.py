import logging
from uuid import uuid4

from boto3 import resource

from django.contrib.auth.models import AbstractUser
from django.db import models

bucket_id = "neighborhoodlostpets.com"
s3 = resource("s3")
logger = logging.getLogger(__name__)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.EmailField("email address", blank=False)


class UserAddress(models.Model):
    user = models.ForeignKey("User", related_name="address", on_delete=models.CASCADE)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    country = models.CharField(max_length=3, default="USA")


class Sex(models.IntegerChoices):
    # These values are based on the ISO/IEC 5218 standard.
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NOT_APPLICABLE = 9


class Animal(models.TextChoices):
    DOG = "Dog"
    CAT = "Cat"
    OTHER = "Other"


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
    name = models.CharField(max_length=50, blank=True, default="")
    animal = models.CharField(max_length=50, choices=Animal.choices)
    breed = models.ManyToManyField("Breed")
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

    user = models.ForeignKey("User", related_name="pets", on_delete=models.CASCADE)
    likes = models.ManyToManyField("User", related_name="likes", blank=True)


class PetLastKnownLocation(models.Model):
    latitude = models.DecimalField(max_digits=8, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    pet = models.OneToOneField(
        "Pet", related_name="last_known_location", on_delete=models.CASCADE
    )


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    order = models.IntegerField(default=0)
    pet = models.ForeignKey("Pet", related_name="photos", on_delete=models.CASCADE)
    file = models.ImageField()


class Comment(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    pet = models.ForeignKey("Pet", on_delete=models.CASCADE)
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    text = models.CharField(max_length=2000)
