from django.test import TestCase
from django.contrib.auth.models import User
from api.tests.mock import mock_user_data, mock_pet_data
from api.models import Pet, Comment
from api.serializers import PetSerializer, UserProfileSerializer, CreateUserSerializer


class UserProfileSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**mock_user_data())
        cls.pet = Pet.objects.create(**mock_pet_data(user=cls.user))
        cls.comment = Comment.objects.create(
            pet=cls.pet, user=cls.user, text="test comment"
        )

    def test_outputs_required_fields(self):
        serializer = UserProfileSerializer(self.user)
        self.assertEqual(len(serializer.data), 5)
        for i in ["username", "email", "first_name", "last_name", "pets"]:
            with self.subTest(field_name=i):
                self.assertIn(i, serializer.data)
        self.assertIsInstance(serializer.data["pets"], list)

    def test_validates_correct_data(self):
        data = {
            "username": "oscar123",
            "email": "oscar@email.com",
            "first_name": "oscar",
            "last_name": "rojas",
        }
        serializer = UserProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validates_incorrect_data(self):
        data = {"first_name": "oscar", "last_name": "rojas"}
        serializer = UserProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class CreateUserSerializerTest(TestCase):
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

    def test_accepts_required_fields(self):
        self.assertTrue(CreateUserSerializer(data=self.valid_data).is_valid())
        self.assertFalse(
            CreateUserSerializer(data=self.data_missing_username).is_valid()
        )
        self.assertFalse(
            CreateUserSerializer(data=self.data_missing_password).is_valid()
        )
        self.assertFalse(CreateUserSerializer(data=self.data_missing_email).is_valid())


class PetSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**mock_user_data())
        cls.pet = Pet.objects.create(**mock_pet_data(user=cls.user))
        cls.comment = Comment.objects.create(
            pet=cls.pet, user=cls.user, text="test comment"
        )
        cls.fields = [
            "id",
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
            "user",
            "likes",
        ]

    def test_outputs_correct_fields(self):
        serializer = PetSerializer(self.pet)
        for field in self.fields:
            with self.subTest(field=field):
                self.assertIn(field, serializer.data)
