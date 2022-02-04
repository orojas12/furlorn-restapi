from api.models import Pet, Photo, UserProfile
from api.serializers import (
    PetSerializer,
    PhotoSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from api.tests.fake_data import fake_image_file, fake_pet_data, fake_user_data
from django.contrib.auth.models import User
from django.test import TestCase


class UserProfileSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**fake_user_data(username="testuser1"))
        cls.profile = UserProfile.objects.create(user=cls.user)

    def test_serializes_required_fields(self):
        serializer = UserProfileSerializer(self.profile)
        for i in ["id", "user", "pets"]:
            self.assertIn(i, serializer.data)
        self.assertIsInstance(serializer.data["pets"], list)


class UserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_data = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
            "password": "apples",
            "email": "oscar@email.com",
        }
        cls.data_missing_username = {
            "first_name": "oscar",
            "last_name": "rojas",
            "password": "apples",
            "email": "oscar@email.com",
        }
        cls.data_missing_password = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
            "email": "oscar@email.com",
        }
        cls.data_missing_email = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
            "password": "apples",
        }

    def test_deserializes_required_fields(self):
        self.assertTrue(UserSerializer(data=self.valid_data).is_valid())
        self.assertFalse(UserSerializer(data=self.data_missing_username).is_valid())
        self.assertFalse(UserSerializer(data=self.data_missing_password).is_valid())
        self.assertFalse(UserSerializer(data=self.data_missing_email).is_valid())


class PetSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(**fake_user_data())
        cls.profile = UserProfile.objects.create(user=user)

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
        data = fake_pet_data(user=self.profile.id, include_location=True)
        data["photos"] = [{"order": 0, "file": fake_image_file()}]
        serializer = PetSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        for field in fields:
            self.assertIn(field, serializer.validated_data)

    def test_deserializes_required_fields(self):
        data = fake_pet_data(
            user=self.profile.id,
            include_location=True,
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
        pet = Pet.objects.create(**fake_pet_data(user=self.profile))
        serializer = PetSerializer(pet)
        for field in fields:
            self.assertIn(field, serializer.data)

        pet = Pet.objects.create(
            **fake_pet_data(
                user=self.profile,
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
        cls.user = UserProfile.objects.create(user=user)
        cls.pet = Pet.objects.create(**fake_pet_data(user=cls.user))
        cls.photo = Photo(pet=cls.pet, file=fake_image_file())
        cls.fields = ["order", "file"]

    def test_serializes_all_fields(self):
        serializer = PhotoSerializer(self.photo)
        self.assertEqual(len(serializer.data), len(self.fields))
        for field in self.fields:
            self.assertTrue(field in serializer.data)

    def test_deserializes_all_fields(self):
        serializer = PhotoSerializer(data={"order": 1, "file": fake_image_file()})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data), len(self.fields))
