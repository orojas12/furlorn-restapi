from api.models import Pet, Photo, User
from api.serializers import (
    PetSerializer,
    PhotoSerializer,
    UserSerializer,
)
from api.tests.fake_data import fake_image_file, fake_pet_data, fake_user_data
from django.test import TestCase


class UserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**fake_user_data(username="testuser1"))

    def test_serializes_required_fields(self):
        serializer = UserSerializer(self.user)
        keys = ["username", "first_name", "last_name", "pets"]
        for key in keys:
            self.assertIn(key, serializer.data)
        self.assertEqual(len(serializer.data), len(keys))

    def test_create(self):
        data = fake_user_data(username="user1")
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, data["username"])

    def test_update(self):
        data = fake_user_data(username="user2")
        serializer = UserSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data["username"])

    def test_partial_update(self):
        data = {"username": "user3"}
        serializer = UserSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data["username"])

    def test_deserializes_required_fields(self):
        valid_data = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
            "password": "apples",
            "email": "oscar@email.com",
        }
        data_missing_username = {
            "first_name": "oscar",
            "last_name": "rojas",
            "password": "apples",
            "email": "oscar@email.com",
        }
        data_missing_password = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
            "email": "oscar@email.com",
        }
        data_missing_email = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
            "password": "apples",
        }
        self.assertTrue(UserSerializer(data=valid_data).is_valid())
        self.assertFalse(UserSerializer(data=data_missing_username).is_valid())
        self.assertFalse(UserSerializer(data=data_missing_password).is_valid())
        self.assertFalse(UserSerializer(data=data_missing_email).is_valid())


class PetSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**fake_user_data())

    def test_deserializes_all_fields(self):
        fields = [
            "name",
            "animal",
            "breed",
            "age",
            "sex",
            "eye_color",
            "color",
            "weight",
            "microchip",
            "information",
            "status",
            "last_known_location",
            "user",
            "photos",
        ]
        data = fake_pet_data(user=self.user, serializable=True)
        data["photos"] = [{"order": 0, "file": fake_image_file()}]
        serializer = PetSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        for field in fields:
            self.assertIn(field, serializer.validated_data)

    def test_deserializes_required_fields(self):
        data = fake_pet_data(
            user=self.user,
            serializable=True,
            exclude=[
                "name",
                "age",
                "sex",
                "eye_color",
                "color",
                "weight",
                "information",
                "microchip",
            ],
        )
        serializer = PetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializes_all_fields(self):
        fields = [
            "name",
            "age",
            "sex",
            "eye_color",
            "color",
            "weight",
            "information",
            "microchip",
            "animal",
            "breed",
            "status",
            "last_known_location",
            "user",
            "photos",
            "likes",
        ]
        pet = Pet.objects.create(**fake_pet_data(user=self.user))
        serializer = PetSerializer(pet)
        for field in fields:
            self.assertIn(field, serializer.data)

        pet = Pet.objects.create(
            **fake_pet_data(
                user=self.user,
                exclude=[
                    "name",
                    "age",
                    "sex",
                    "eye_color",
                    "color",
                    "weight",
                    "information",
                    "microchip",
                ],
            )
        )
        serializer = PetSerializer(pet)
        for field in fields:
            self.assertIn(field, serializer.data)


class PhotoSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(**fake_user_data())
        cls.pet = Pet.objects.create(**fake_pet_data(user=user))
        cls.photo = Photo(pet=cls.pet, file=fake_image_file())
        cls.fields = ["order", "file"]

    def test_serializes_all_fields(self):
        serializer = PhotoSerializer(self.photo)
        self.assertEqual(len(serializer.data), len(self.fields))
        for field in self.fields:
            self.assertTrue(field in serializer.data)

    def test_deserializes_all_fields(self):
        serializer = PhotoSerializer(data={"order": 1, "file": fake_image_file()})
        serializer.is_valid()
        print(serializer.errors)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data), len(self.fields))
