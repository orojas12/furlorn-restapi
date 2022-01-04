from uuid import uuid4

from api.models import Animal, Sex, Pet


def mock_pet_data(user):
    fields = {
        "name": "Yuna",
        "animal": Animal.CAT,
        "age": 2,
        "sex": Sex.FEMALE,
        "eye_color": Pet.Color.YELLOW,
        "color": Pet.Color.BROWN,
        "weight": 8,
        "microchip": "900123456789000",
        "information": "last seen on 5th",
        "status": Pet.Status.LOST,
        "user": user,
    }
    return fields


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
