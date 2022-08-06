import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

logger = logging.getLogger(__name__)


class User(AbstractUser):
    nickname = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return self.username


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


class Species(models.TextChoices):
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


class Breed(models.Model):
    name = models.CharField(max_length=50)
    species = models.CharField(max_length=50, choices=Species.choices)


class Color(models.Model):
    name = models.CharField(max_length=50)

    # Only 6-digit hex is stored (#AABBCC) without leading '#' digit
    # May store trailing alpha byte (00-FF) in the future
    hex = models.CharField(max_length=8)


class Pet(models.Model):
    name = models.CharField(max_length=50, blank=True, default="")
    species = models.CharField(max_length=50, choices=Species.choices)
    breed = models.ManyToManyField("Breed")
    age = models.PositiveIntegerField(blank=True, null=True)
    sex = models.IntegerField(choices=Sex.choices, blank=True, default=Sex.UNKNOWN)
    eye_colors = models.ManyToManyField("Color", related_name="pet_eye_colors")
    coat_colors = models.ManyToManyField("Color", related_name="pet_coat_colors")
    weight = models.PositiveIntegerField(blank=True, null=True)
    microchip = models.CharField(max_length=15, blank=True, default="")


class Post(models.Model):
    class Status(models.TextChoices):
        LOST = "lost"
        FOUND = "found"
        RESOLVED = "resolved"

    description = models.CharField(max_length=5000, default="")
    likes = models.PositiveIntegerField(default=0)
    location_lat = models.DecimalField(max_digits=8, decimal_places=6)
    location_long = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=50, choices=Status.choices)
    pet = models.ForeignKey("Pet", related_name="posts", on_delete=models.CASCADE)
    user = models.ForeignKey("User", related_name="posts", on_delete=models.CASCADE)


class Photo(models.Model):
    order = models.IntegerField()
    post = models.ForeignKey("Post", related_name="photos", on_delete=models.CASCADE)
    file = models.ImageField()


class Comment(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    content = models.CharField(max_length=2000)
