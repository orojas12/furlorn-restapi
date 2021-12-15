from django.db import models
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User


class Sex(models.IntegerChoices):
    # These values are based on the ISO/IEC 5218 standard.
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NOT_APPLICABLE = 9


class Animal(models.IntegerChoices):
    UNKNOWN = 0
    DOG = 1
    CAT = 2


class Breed(models.Model):
    name = models.CharField(max_length=50)
    animal = models.IntegerField(choices=Animal.choices)


class Pet(models.Model):
    class Color(models.IntegerChoices):
        UNKNOWN = 0
        WHITE = 1
        BLACK = 2
        BROWN = 3
        ORANGE = 4
        RED = 5
        PINK = 6
        PURPLE = 7
        BLUE = 8
        GREEN = 9
        YELLOW = 10
        GRAY = 11

    class Status(models.IntegerChoices):
        UNKNOWN = 0
        LOST = 1
        FOUND = 2
        REUNITED = 3

    name = models.CharField(max_length=50)
    animal = models.IntegerField(choices=Animal.choices)
    breed = models.ManyToManyField("Breed", blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    sex = models.IntegerField(choices=Sex.choices, blank=True, default=Sex.UNKNOWN)
    eye_color = models.IntegerField(
        choices=Color.choices, blank=True, default=Color.UNKNOWN
    )
    exterior_color = models.IntegerField(
        choices=Color.choices, blank=True, default=Color.UNKNOWN
    )
    weight = models.PositiveIntegerField(blank=True, null=True)
    information = models.CharField(max_length=5000, blank=True)
    status = models.IntegerField(choices=Status.choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Photo(models.Model):
    url = CharField(max_length=200)
    pet = ForeignKey("Pet", on_delete=models.CASCADE)


# class User(models.Model):
#     id = models.UUIDField(primary_key=True, blank=True, default=uuid4)
#     name = models.CharField(max_length=50)
#     surname = models.CharField(max_length=50, blank=True)
#     email = models.EmailField()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey("Pet", on_delete=models.CASCADE)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey("Pet", on_delete=models.CASCADE)
    reply_to = models.ForeignKey("self", on_delete=models.CASCADE, blank=True)
