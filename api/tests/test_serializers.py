from api.models import Pet, Photo, User, Post
from api.serializers import (
    ChangePasswordSerializer,
    LoginUserSerializer,
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
        fields = ["username", "first_name", "last_name", "email", "posts"]
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
        valid_data = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
            "email": "oscar@email.com",
        }
        data_missing_username = {
            "first_name": "oscar",
            "last_name": "rojas",
            "email": "oscar@email.com",
        }
        data_missing_email = {
            "username": "oscar123",
            "first_name": "oscar",
            "last_name": "rojas",
        }
        valid_data_missing_first_last_name = {
            "username": "oscar123",
            "email": "oscar@email.com",
        }
        self.assertTrue(UserSerializer(data=valid_data).is_valid())
        self.assertFalse(UserSerializer(data=data_missing_username).is_valid())
        self.assertTrue(
            UserSerializer(data=valid_data_missing_first_last_name).is_valid()
        )
        self.assertFalse(UserSerializer(data=data_missing_email).is_valid())


class PetSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pet = Pet.objects.create(**FakePet().data)
        cls.fields = [
            "id",
            "name",
            "type",
            "breed",
            "age",
            "sex",
            "eye_color",
            "color",
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
        cls.fields = ["username", "password", "email", "first_name", "last_name"]

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
        fields = ["username", "first_name", "last_name"]
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


class LoginUserSerializerTest(TestCase):
    def test_returns_correct_fields(self):
        user_data = FakeUser().data
        serializer = LoginUserSerializer(
            data={
                "username": user_data["username"],
                "password": user_data["password"],
            }
        )
        serializer.is_valid(raise_exception=True)
        self.assertIn("username", serializer.data)
        self.assertEqual(len(serializer.data), 1)
