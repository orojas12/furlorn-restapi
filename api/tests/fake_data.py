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
        self.color = Pet.Color.BROWN
        self.weight = 8
        self.microchip = "900123456789000"
        super().__init__(**kwargs)


class FakeUser(FakeData):
    def __init__(self, **kwargs):
        # Use a random string for the username to ensure uniqueness between tests.
        id = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        self.username = f"user_{id}"
        self.first_name = "Bob"
        self.last_name = "Dylan"
        self.email = "bob@gmail.com"
        self.password = fake_password()
        super().__init__(**kwargs)


class FakePost(FakeData):
    def __init__(self, **kwargs):
        self.description = "post description"
        self.location_lat = 20
        self.location_long = 25
        self.status = "lost"
        super().__init__(**kwargs)


def fake_pet_data(
    user, serializable=False, exclude: list = [], format="json", **kwargs
):
    """
    Generate pet data for creating model instances and serializers.


    """
    location = {"latitude": 31.811348, "longitude": -106.564600}

    fields = [
        {"name": "name", "default": "Yuna"},
        {"name": "species", "default": Species.CAT},
        {"name": "age", "default": 2},
        {"name": "sex", "default": Sex.FEMALE},
        {"name": "eye_color", "default": Pet.Color.YELLOW},
        {"name": "color", "default": Pet.Color.BROWN},
        {"name": "weight", "default": 8},
        {"name": "microchip", "default": "900123456789000"},
        {"name": "information", "default": "last seen on 5th"},
        {
            "name": "last_known_location",
            "default": PetLastKnownLocation(
                latitude=location["latitude"], longitude=location["longitude"]
            ),
        },
        {"name": "status", "default": Pet.Status.LOST},
        {"name": "user", "default": user},
    ]

    serializable_defaults = {
        "last_known_location": {
            "json": location,
            # Multipart form data doesn't support nested structures,
            # so this field's value is converted to a json string.
            "multipart": json.dumps(location),
        },
        "user": {
            "json": user.id,
            "multipart": user.id,
        },
    }

    data = dict()
    fields = list(filter(lambda field: field["name"] not in exclude, fields))

    if serializable:
        # Change the value of non-serializable fields
        # to one that is serializable.
        for field in fields:
            field_name = field["name"]
            if field_name in serializable_defaults:
                field["default"] = serializable_defaults[field_name][format]

    # Populate final data with remaining fields and their values
    # specified in kwargs or their default values.
    for field in fields:
        data[field["name"]] = kwargs.get(field["name"], field["default"])

    return data


def fake_user_data(exclude: list = [], **kwargs) -> dict:
    """Generate user data for testing."""

    # Use a random string for the username to ensure uniqueness between tests.
    id = "".join(random.choices(string.ascii_letters + string.digits, k=6))

    final_data = dict()

    fields = [
        {"name": "username", "default": f"user_{id}"},
        {"name": "first_name", "default": "oscar"},
        {"name": "last_name", "default": "rojas"},
        {"name": "email", "default": "oscar@email.com"},
        {"name": "password", "default": fake_password()},
    ]

    # Filter out fields that should be excluded from result.
    fields = list(filter(lambda field: field["name"] not in exclude, fields))

    # Populate final data with remaining fields and their values
    # specified in kwargs or their default values.
    for field in fields:
        final_data[field["name"]] = kwargs.get(field["name"], field["default"])

    return final_data


def fake_image_file():
    image = BytesIO()
    Image.new("RGB", (100, 100)).save(image, "JPEG")
    image.seek(0)
    return SimpleUploadedFile(f"img_{str(uuid4())}.jpg", image.getvalue(), "image/jpeg")


def fake_password(length=8):
    """Generate a random string that can be used as a valid user password for testing."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
