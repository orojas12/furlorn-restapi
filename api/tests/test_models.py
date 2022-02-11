from uuid import UUID

import boto3
from api.models import (
    Animal,
    Breed,
    Comment,
    Pet,
    PetLastKnownLocation,
    Photo,
    UserAddress,
    User,
)
from api.tests.fake_data import fake_pet_data, fake_image_file, fake_user_data
from django.core.files.base import File
from django.test import TestCase
from neighborhood_lost_pets.settings import BASE_DIR

S3 = boto3.resource("s3")
BUCKET_ID = "neighborhoodlostpets.com"
TEST_DIR = BASE_DIR / "api/tests"


class PetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # add likes to pets
        user1 = User.objects.create(**fake_user_data(username="user1"))
        user2 = User.objects.create(**fake_user_data(username="user2"))
        cls.pet1 = Pet.objects.create(**fake_pet_data(user=user1))
        cls.pet2 = Pet.objects.create(**fake_pet_data(user=user1))
        cls.pet1.likes.add(user1)
        cls.pet1.likes.add(user2)
        cls.pet2.likes.add(user1)
        cls.pet2.likes.add(user2)

    def test_it_has_correct_fields(self):
        pet = self.pet1
        self.assertIsInstance(pet.id, UUID)
        self.assertIsInstance(pet.name, str)
        self.assertIsInstance(pet.animal, str),
        self.assertIsInstance(pet.age, int)
        self.assertIsInstance(pet.sex, int)
        self.assertIsInstance(pet.eye_color, str)
        self.assertIsInstance(pet.color, str)
        self.assertIsInstance(pet.weight, int)
        self.assertIsInstance(pet.microchip, str)
        self.assertIsInstance(pet.information, str)
        self.assertIsInstance(pet.status, str)
        self.assertIsInstance(pet.user, User)

    def test_many_to_many_relationship(self):
        self.assertEqual(self.pet1.likes.count(), 2)
        self.assertEqual(self.pet2.likes.count(), 2)


class PetLastKnownLocationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(**fake_user_data())
        pet = Pet.objects.create(**fake_pet_data(user=user))
        cls.location = PetLastKnownLocation.objects.create(
            pet=pet, latitude=31.811348, longitude=-106.564600
        )

    def test_it_has_correct_fields(self):
        location = self.location
        self.assertIsInstance(location.latitude, float)
        self.assertIsInstance(location.longitude, float)
        self.assertIsInstance(location.pet, Pet)


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**fake_user_data())

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.user.id, UUID)
        self.assertIsInstance(self.user.username, str)
        self.assertIsInstance(self.user.email, str)
        self.assertIsInstance(self.user.first_name, str)
        self.assertIsInstance(self.user.last_name, str)


class UserAddressModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        address_data = {
            "street": "123 Test St",
            "city": "El Paso",
            "state": "TX",
            "zip": "79901",
            "country": "USA",
        }
        user = User.objects.create(**fake_user_data())
        cls.address = UserAddress.objects.create(user=user, **address_data)

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.address.user, User)
        self.assertIsInstance(self.address.street, str)
        self.assertIsInstance(self.address.city, str)
        self.assertIsInstance(self.address.state, str)
        self.assertIsInstance(self.address.zip, str)
        self.assertIsInstance(self.address.country, str)


class BreedModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Breed.objects.create(
            name="American Shorthair",
            animal=Animal.CAT,
        )

    def test_it_has_correct_fields(self):
        breed = Breed.objects.all().first()
        self.assertIsInstance(breed.name, str)
        self.assertIsInstance(breed.animal, str)


class PhotoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="user1")
        cls.pet = Pet.objects.create(**fake_pet_data(user=user))
        cls.photo = Photo(
            pet=cls.pet,
            order=0,
            file=fake_image_file(),
        )

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.photo.id, UUID)
        self.assertIsInstance(self.photo.order, int)
        self.assertIsInstance(self.photo.file, File)
        self.assertIsInstance(self.photo.pet, Pet)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = []
        for i in range(3):
            cls.users.append(
                User.objects.create(**fake_user_data(username=f"user_{i}"))
            )

        pet = Pet.objects.create(**fake_pet_data(user=cls.users[0]))

        for user in cls.users:
            comment = Comment.objects.create(user=user, pet=pet, text="comment")
            Comment.objects.create(
                user=user,
                pet=pet,
                reply_to=comment,
                text="reply",
            )

    def test_it_has_correct_fields(self):
        comment = Comment.objects.all().first()
        self.assertIsInstance(comment.user, User)
        self.assertIsInstance(comment.pet, Pet)
        self.assertIsInstance(comment.text, str)

    def test_self_reference(self):
        for comment in Comment.objects.filter(reply_to=None):
            reply = Comment.objects.filter(reply_to=comment).first()
            self.assertEquals(comment, reply.reply_to)
