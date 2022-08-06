from unittest.mock import MagicMock, patch
from api.models import Breed, Pet, Photo, Species, User, Post
from api.serializers import (
    ChangePasswordSerializer,
    CreatePostSerializer,
    PetSerializer,
    PhotoSerializer,
    UserSerializer,
    RegisterUserSerializer,
)
from api.tests.fake_data import (
    FakeUser,
    FakePet,
    FakePost,
    fake_image_file,
    fake_password,
)
from django.test import TestCase


class UserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**FakeUser().data)

    def test_returns_correct_fields(self):
        """
        Test that UserSerializer.data returns the specified fields only.
        """
        serializer = UserSerializer(self.user)
        fields = ["username", "nickname", "posts"]
        for field in fields:
            self.assertIn(field, serializer.data)
        self.assertEqual(len(serializer.data), len(fields))

    def test_update_user(self):
        """
        Test that UserSerializer updates a user successfully.
        """
        data = FakeUser().exclude("password")
        serializer = UserSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data["username"])

    def test_validation(self):
        """
        Test that UserSerializer properly validates all fields.
        """
        username_and_nickname = {
            "username": "oscar123",
            "nickname": "oscar",
        }
        nickname = {
            "nickname": "oscar",
        }
        username = {
            "username": "oscar123",
        }
        self.assertTrue(UserSerializer(data=username_and_nickname).is_valid())
        self.assertFalse(UserSerializer(data=nickname).is_valid())
        self.assertTrue(UserSerializer(data=username).is_valid())


class PetSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pet = Pet.objects.create(**FakePet().data)
        cls.fields = [
            "id",
            "name",
            "species",
            "breed",
            "age",
            "sex",
            "eye_colors",
            "coat_colors",
            "weight",
            "microchip",
        ]

    def test_returns_correct_fields(self):
        """
        Test that PetSerializer.data returns the specified fields only.
        """
        serializer = PetSerializer(instance=self.pet)
        for field in self.fields:
            self.assertIn(field, serializer.data)
        self.assertEqual(len(self.fields), len(serializer.data))

    def test_deserializes_all_fields(self):
        serializer = PetSerializer(data=FakePet().data)
        self.assertTrue(serializer.is_valid())


class PhotoSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(**FakeUser().data)
        pet = Pet.objects.create(**FakePet().data)
        post = Post.objects.create(user=user, pet=pet, **FakePost().data)
        cls.photo = Photo(post=post, file=fake_image_file())
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


class RegisterUserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = FakeUser().data
        cls.fields = ["username", "password", "nickname"]

    def test_registers_user(self):
        """
        Test that RegisterUserSerializer successfully registers a user.
        """
        serializer = RegisterUserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(
            self.user_data["username"], User.objects.all().first().username
        )

    def test_returns_correct_fields(self):
        """
        Test that RegisterUserSerializer.data returns the specified fields only.
        """
        serializer = RegisterUserSerializer(data=FakeUser().data)
        serializer.is_valid(raise_exception=True)
        fields = ["username", "nickname"]
        for field in fields:
            self.assertIn(field, serializer.data)
        self.assertEqual(len(serializer.data), len(fields))


class ChangePasswordSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_data = FakeUser().data
        cls.old_password = user_data["password"]
        cls.new_password = fake_password()
        cls.user = User.objects.create_user(**user_data)

    def test_changes_password(self):
        """
        Test that ChangePasswordSerializer successfully changes a user's password.
        """
        serializer = ChangePasswordSerializer(
            instance=self.user,
            data={
                "old_password": self.old_password,
                "new_password": self.new_password,
            },
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(self.user.check_password(self.new_password))


class CreatePostSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fields = [
            "description",
            "location_lat",
            "location_long",
            "status",
            "pet",
            "photos",
        ]
        cls.user = User.objects.create(**FakeUser().data)
        cls.cat_breeds = Breed.objects.filter(species=Species.CAT)
        cls.dog_breeds = Breed.objects.filter(species=Species.DOG)
        cls.pet_data = FakePet().data
        cls.post_data = FakePost().data
        cls.data = {
            "pet": {
                "breed": [cls.cat_breeds[0].id, cls.cat_breeds[1].id],
                **cls.pet_data,
            },
            "photos": [
                {"order": 0, "file": fake_image_file()},
                {"order": 1, "file": fake_image_file()},
            ],
            **cls.post_data,
        }

    def test_deserializes_fields(self):
        serializer = CreatePostSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(len(serializer.validated_data), len(self.fields))

    @patch("api.models.Photo.objects.create")
    def test_creates_post(
        self,
        mock_photo_create: MagicMock,
    ):
        serializer = CreatePostSerializer(data=self.data, context={"user": self.user})
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        pet = Pet.objects.all().first()
        self.assertEqual(post, Post.objects.all().first())
        self.assertEqual(post.pet, pet)
        self.assertEqual(pet.breed.count(), 2)
        self.assertEqual(mock_photo_create.call_count, 2)
