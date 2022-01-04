from uuid import uuid4

from api.models import Animal, Sex, Pet


def mock_pet_data(exclude: list = None, **kwargs):
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
        {"name": "status", "default": Pet.Status.LOST},
        {"name": "user", "default": 1},
    ]

    data = dict()

    if exclude:
        for field in fields:
            if field["name"] in exclude:
                fields.remove(field)

    for field in fields:
        data[field["name"]] = kwargs.get(field["name"], field["default"])

    return data


def mock_user_data(partial=False, **kwargs):
    user = {
        "username": ("oscar" if not kwargs.get("username") else kwargs["username"]),
        "first_name": "oscar",
        "last_name": "rojas",
        "email": "oscar@email.com",
        "password": "apples",
    }
    if partial:
        user = {**kwargs}
    return user
