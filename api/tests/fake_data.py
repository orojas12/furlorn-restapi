from abc import ABC, abstractmethod, abstractproperty
from io import BytesIO
import json
import random
import string
from uuid import uuid4
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import Species, Sex, Pet


class FakeData:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.fields = []
        for key in self.__dict__:
            if key != "kwargs" and key != "fields":
                self.fields.append(key)

    @property
    def data(self) -> dict:
        data = dict()
        for field in self.fields:
            data[field] = self.kwargs.get(field, getattr(self, field))
        return data

    def exclude(self, fields=[]) -> dict:
        return {key: value for (key, value) in self.data.items() if key not in fields}


class FakePet(FakeData):
    def __init__(self, **kwargs):
        self.name = "Yuna"
        self.species = "Cat"
        self.age = 2
        self.sex = Sex.FEMALE
        self.eye_color = Pet.Color.YELLOW
        self.coat_color = Pet.Color.BROWN
        self.weight = 8
        self.microchip = "900123456789000"
        super().__init__(**kwargs)


class FakeUser(FakeData):
    def __init__(self, **kwargs):
        # Use a random string for the username to ensure uniqueness between tests.
        id = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        self.username = f"user_{id}"
        self.nickname = "Bob"
        self.password = fake_password()
        super().__init__(**kwargs)


class FakePost(FakeData):
    def __init__(self, **kwargs):
        self.description = "post description"
        self.location_lat = 20
        self.location_long = 25
        self.status = "lost"
        super().__init__(**kwargs)


def fake_image_file():
    image = BytesIO()
    Image.new("RGB", (100, 100)).save(image, "JPEG")
    image.seek(0)
    return SimpleUploadedFile(f"img_{str(uuid4())}.jpg", image.getvalue(), "image/jpeg")


def fake_password(length=8):
    """Generate a random string that can be used as a valid user password for testing."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
