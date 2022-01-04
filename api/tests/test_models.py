import logging
from uuid import UUID

import boto3
from api.models import Animal, Breed, Comment, Pet, Photo
from api.tests.mock import mock_pet_data
from botocore.exceptions import ClientError
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status

from neighborhood_lost_pets.settings import BASE_DIR

S3 = boto3.resource("s3")
BUCKET_ID = "neighborhoodlostpets.com"
TEST_DIR = BASE_DIR / "api/tests"


class PetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create 3 users and 3 pets (pet.user does not matter here)
        for i in range(3):
            User.objects.create(username=f"oscar{i}")
        for i in range(3):
            Pet.objects.create(**mock_pet_data(User.objects.all().first()))
        # add likes to pets
        for pet in Pet.objects.all():
            for user in User.objects.all():
                pet.likes.add(user)

    def test_it_has_correct_fields(self):
        pet = Pet.objects.all().first()
        self.assertIsInstance(pet.name, str)
        self.assertIsInstance(pet.animal, int),
        self.assertIsInstance(pet.age, int)
        self.assertIsInstance(pet.sex, int)
        self.assertIsInstance(pet.eye_color, str)
        self.assertIsInstance(pet.color, str)
        self.assertIsInstance(pet.weight, int)
        self.assertIsInstance(pet.microchip, str)
        self.assertIsInstance(pet.information, str)
        self.assertIsInstance(pet.status, int)
        self.assertIsInstance(pet.user, User)

    def test_many_to_one_relationship(self):
        pets = Pet.objects.all()
        user = User.objects.all().first()
        self.assertEquals(len(pets), user.pets.count())
        for pet in pets:
            self.assertIn(pet, user.pets.all())

    def test_many_to_many_relationship(self):
        for user in User.objects.all():
            for pet in user.likes.all():
                self.assertIn(user, pet.likes.all())

        for pet in Pet.objects.all():
            for user in pet.likes.all():
                self.assertIn(pet, user.likes.all())


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
        self.assertIsInstance(breed.animal, int)


class PhotoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username="oscar")
        cls.pet = Pet.objects.create(**mock_pet_data(cls.user))
        with open(TEST_DIR / "images/dog.jpg", "rb") as f:
            cls.photo = Photo.objects.create(
                url="http://myphotourl.com/123",
                pet=cls.pet,
                file_stream=f.read(),
                content_type="image/jpeg",
            )

    @classmethod
    def tearDownClass(cls) -> None:
        s3_obj = S3.Object(BUCKET_ID, str(cls.photo.id))
        s3_obj.delete()

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.photo.id, UUID),
        self.assertIsInstance(self.photo.url, str),
        self.assertIsInstance(self.photo.pet, Pet)

    def test_many_to_one_relationship(self):
        self.assertEquals(1, self.pet.photo_set.count())
        self.assertIn(self.photo, self.pet.photo_set.all())

    def test_puts_s3_object(self):
        s3_obj = S3.Object(BUCKET_ID, str(self.photo.id))
        self.assertTrue(self.s3_object_exists(s3_obj))

    def s3_object_exists(self, s3_obj):
        try:
            response = s3_obj.get()
        except ClientError as e:
            logging.debug(e.__str__())
            response = e.response
        finally:
            return response["ResponseMetadata"]["HTTPStatusCode"] == status.HTTP_200_OK


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(3):
            User.objects.create(username=f"oscar{i}")
        pet = Pet.objects.create(**mock_pet_data(user=User.objects.all().first()))
        for user in User.objects.all():
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
