from io import BytesIO
import json
from uuid import uuid4
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import Animal, PetLastKnownLocation, Sex, Pet


def fake_pet_data(
    user, serializable=False, exclude: list = None, format="json", **kwargs
):

    location = {"latitude": 31.811348, "longitude": -106.564600}

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
            "default": PetLastKnownLocation(
                latitude=location["latitude"], longitude=location["longitude"]
            ),
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

    if serializable:
        # Change any field's non-serializable default value
        # to one that is serializable.
        for field in fields:
            if field["name"] == "last_known_location":
                if format == "json":
                    field["default"] = {
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                    }
                elif format == "multipart":
                    # Multipart form data doesn't support nested data,
                    # so this field's value is converted to a json string.
                    field["default"] = json.dumps(
                        {
                            "latitude": location["latitude"],
                            "longitude": location["longitude"],
                        }
                    )
            if field["name"] == "user":
                field["default"] = str(user.id)

    for field in fields_to_remove:
        fields.remove(field)

    for field in fields:
        # Populate final data with remaining fields and their values
        # specified in kwargs or their default values.
        data[field["name"]] = kwargs.get(field["name"], field["default"])

    return data


def fake_user_data(exclude: list = None, **kwargs):
    id = str(uuid4())

    fields = [
        {"name": "username", "default": f"user_{id}"},
        {"name": "first_name", "default": "oscar"},
        {"name": "last_name", "default": "rojas"},
        {"name": "email", "default": "oscar@email.com"},
        {"name": "password", "default": "apples"},
    ]

    data = dict()
    fields_to_remove = []
    if exclude:
        for field in fields:
            if field["name"] in exclude:
                fields_to_remove.append(field)

    for field in fields_to_remove:
        fields.remove(field)

    for field in fields:
        data[field["name"]] = kwargs.get(field["name"], field["default"])

    return data


def fake_image_file():
    image = BytesIO()
    Image.new("RGB", (100, 100)).save(image, "JPEG")
    image.seek(0)
    return SimpleUploadedFile(f"img_{str(uuid4())}.jpg", image.getvalue(), "image/jpeg")
