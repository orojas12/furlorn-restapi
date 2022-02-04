from io import BytesIO
from uuid import uuid4
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import Animal, Sex, Pet


def fake_pet_data(user, include_location=False, exclude: list = None, **kwargs):
    fields = [
        {"name": "name", "default": "Yuna"},
        {"name": "animal", "default": Animal.CAT},
        {"name": "age", "default": 2},
        {"name": "sex", "default": Sex.FEMALE},
        {"name": "eye_color", "default": Pet.Color.YELLOW},
        {"name": "color", "default": Pet.Color.BROWN},
        {"name": "weight", "default": 8},
        {"name": "microchip", "default": "900123456789000"},
        {"name": "information", "default": "last seen on 5th"},
        {
            "name": "last_known_location",
            "default": {"latitude": 31.811348, "longitude": -106.564600},
        },
        {"name": "status", "default": Pet.Status.LOST},
        {"name": "user", "default": user},
    ]

    data = dict()
    fields_to_remove = []
    if exclude:
        for field in fields:
            if field["name"] in exclude:
                fields_to_remove.append(field)

    if not include_location:
        for field in fields:
            if field["name"] == "last_known_location":
                fields_to_remove.append(field)

    for field in fields_to_remove:
        fields.remove(field)

    for field in fields:
        data[field["name"]] = kwargs.get(field["name"], field["default"])

    return data


def fake_user_data(partial=False, **kwargs):
    user = {
        "username": ("user1" if not kwargs.get("username") else kwargs["username"]),
        "first_name": "oscar",
        "last_name": "rojas",
        "email": "oscar@email.com",
        "password": "apples",
    }
    if partial:
        user = {**kwargs}
    return user


def fake_image_file():
    image = BytesIO()
    Image.new("RGB", (100, 100)).save(image, "JPEG")
    image.seek(0)
    return SimpleUploadedFile("test.jpg", image.getvalue(), "image/jpeg")
