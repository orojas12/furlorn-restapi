from uuid import UUID

import boto3
from api.models import (
    Animal,
    Breed,
    Comment,
    Post,
    Pet,
    Photo,
    UserAddress,
    User,
)
from api.tests.fake_data import (
    FakeUser,
    FakePet,
    FakePost,
    fake_image_file,
)
from django.core.files.base import File
from django.test import TestCase
from neighborhood_lost_pets.settings import BASE_DIR

S3 = boto3.resource("s3")
BUCKET_ID = "neighborhoodlostpets.com"
TEST_DIR = BASE_DIR / "api/tests"


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**FakeUser().data)
        pet = Pet.objects.create(**FakePet().data)
        cls.post = Post.objects.create(pet=pet, user=user, **FakePost().data)
        Photo.objects.create(post=cls.post, order=0, file=fake_image_file())

    def test_it_has_correct_fields(self):
        post = self.post
        self.assertIsInstance(post.id, int)
        self.assertIsInstance(post.user, User)
        self.assertIsInstance(post.pet, Pet)
        self.assertIsInstance(post.description, str)
        self.assertIsInstance(post.likes, int)


class PetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pet = Pet.objects.create(**FakePet().data)

    def test_it_has_correct_fields(self):
        pet = self.pet
        self.assertIsInstance(pet.id, int)
        self.assertIsInstance(pet.name, str)
        self.assertIsInstance(pet.type, str),
        self.assertIsInstance(pet.age, int)
        self.assertIsInstance(pet.sex, int)
        self.assertIsInstance(pet.eye_color, str)
        self.assertIsInstance(pet.color, str)
        self.assertIsInstance(pet.weight, int)
        self.assertIsInstance(pet.microchip, str)


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**FakeUser().data)

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.user.id, int)
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
        user = User.objects.create(**FakeUser().data)
        cls.address = UserAddress.objects.create(user=user, **address_data)

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.address.id, int)
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
        self.assertIsInstance(breed.id, int)
        self.assertIsInstance(breed.name, str)
        self.assertIsInstance(breed.animal, str)


class PhotoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**FakeUser().data)
        pet = Pet.objects.create(**FakePet().data)
        cls.post = Post.objects.create(user=user, pet=pet, **FakePost().data)
        cls.photo = Photo(
            post=cls.post,
            order=0,
            file=fake_image_file(),
        )

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.photo.order, int)
        self.assertIsInstance(self.photo.file, File)
        self.assertIsInstance(self.photo.post, Post)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = []
        for i in range(3):
            cls.users.append(User.objects.create_user(**FakeUser().data))

        pet = Pet.objects.create(**FakePet().data)
        post = Post.objects.create(user=cls.users[0], pet=pet, **FakePost().data)

        for user in cls.users:
            comment = Comment.objects.create(user=user, post=post, content="comment")
            Comment.objects.create(
                user=user,
                post=post,
                reply_to=comment,
                content="reply",
            )

    def test_it_has_correct_fields(self):
        comment = Comment.objects.all().first()
        self.assertIsInstance(comment.id, int)
        self.assertIsInstance(comment.user, User)
        self.assertIsInstance(comment.post, Post)
        self.assertIsInstance(comment.content, str)

    def test_self_reference(self):
        for comment in Comment.objects.filter(reply_to=None):
            reply = Comment.objects.filter(reply_to=comment).first()
            self.assertEquals(comment, reply.reply_to)
