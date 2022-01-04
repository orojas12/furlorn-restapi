from django.test import TestCase
from django.contrib.auth.models import User
from api.tests.mock import mock_user_data, mock_pet_data
from api.models import Pet, Comment, Photo
from api.serializers import PetSerializer, UserProfileSerializer, CreateUserSerializer
from api.tests.test_models import BUCKET_ID, S3, TEST_DIR


class UserProfileSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**mock_user_data(username="testuser1"))
        cls.pet = Pet.objects.create(**mock_pet_data(user=cls.user))
        cls.comment = Comment.objects.create(
            pet=cls.pet, user=cls.user, text="test comment"
        )

    def test_serializes_required_fields(self):
        serializer = UserProfileSerializer(self.user)
        self.assertEqual(len(serializer.data), 5)
        for i in ["username", "email", "first_name", "last_name", "pets"]:
            with self.subTest(field_name=i):
                self.assertIn(i, serializer.data)
        self.assertIsInstance(serializer.data["pets"], list)

    def test_deserializes_correct_data(self):
        data = {
            "username": "oscar123",
            "email": "oscar@email.com",
            "first_name": "oscar",
            "last_name": "rojas",
        }
        serializer = UserProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_does_not_deserialize_incorrect_data(self):
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

    def test_deserializes_required_fields(self):
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
        cls.user = User.objects.create(**mock_user_data(username="testuser2"))
        cls.pet = Pet.objects.create(**mock_pet_data(user=cls.user))
        with open(TEST_DIR / "images/dog.jpg", "rb") as f:
            cls.photo = Photo.objects.create(
                url="http://myphotourl.com/123",
                pet=cls.pet,
                file_stream=f.read(),
                content_type="image/jpeg",
            )
        cls.comment = Comment.objects.create(
            pet=cls.pet, user=cls.user, text="test comment"
        )
        cls.serialized_fields = [
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
            "photos",
        ]
        cls.required_fields = [
            "name",
            "animal",
            "status",
        ]
        cls.optional_fields = [
            "breed",
            "age",
            "sex",
            "eye_color",
            "color",
            "information",
            "weight",
            "microchip",
        ]
        cls.valid_data = mock_pet_data()

    def test_serializes_correct_fields(self):
        serializer = PetSerializer(self.pet)
        for field in self.serialized_fields:
            with self.subTest(field=field):
                self.assertIn(field, serializer.data)

    def test_deserializes_required_fields(self):
        serializer = PetSerializer(data=mock_pet_data(exclude=self.optional_fields))
        self.assertTrue(serializer.is_valid())

    def test_deserializes_optional_fields(self):
        serializer = PetSerializer(data=mock_pet_data())
        self.assertTrue(serializer.is_valid())

    def test_does_not_deserialize_incorrect_data(self):
        for field in self.required_fields:
            data = mock_pet_data(exclude=[field])
            serializer = PetSerializer(data=data)
            self.assertFalse(serializer.is_valid())

    def test_serializes_related_fields(self):
        serializer = PetSerializer(self.pet)
        self.assertEqual(len(serializer.data["photos"]), 1)
        self.assertIn(self.photo.url, serializer.data["photos"])

    @classmethod
    def tearDownClass(cls):
        s3_obj = S3.Object(BUCKET_ID, str(cls.photo.id))
        s3_obj.delete()
