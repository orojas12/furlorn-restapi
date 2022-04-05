from api.models import Pet, Photo, User
from api.serializers import (
    ChangePasswordSerializer,
    PetSerializer,
    PhotoSerializer,
    UserSerializer,
    RegisterUserSerializer,
)
from api.tests.fake_data import (
    fake_image_file,
    fake_password,
    fake_pet_data,
    fake_user_data,
)
from django.test import TestCase


class UserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**fake_user_data())

    def test_returns_correct_fields(self):
        """
        Test that UserSerializer.data returns the specified fields only.
        """
        serializer = UserSerializer(self.user)
        fields = ["username", "first_name", "last_name", "email", "pets"]
        for field in fields:
            self.assertIn(field, serializer.data)
        self.assertEqual(len(serializer.data), len(fields))

    def test_update_user(self):
        """
        Test that UserSerializer updates a user successfully.
        """
        data = fake_user_data(exclude=["password"])
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
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data), len(self.fields))


class RegisterUserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = fake_user_data()
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
        serializer = RegisterUserSerializer(data=fake_user_data())
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        fields = ["username", "first_name", "last_name"]
        for field in fields:
            self.assertIn(field, serializer.data)
        self.assertEqual(len(serializer.data), len(fields))


class ChangePasswordSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_data = fake_user_data()
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
