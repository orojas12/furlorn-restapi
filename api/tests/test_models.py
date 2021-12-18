from django.test import TestCase
from django.contrib.auth.models import User

from api.models import Comment, Pet, Animal, Photo, Breed
from api.tests.mock import mock_pet_data


# Create your tests here.
class PetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create 3 users and 3 pets (pet.user does not matter here)
        for i in range(3):
            User.objects.create(username=f"oscar{i}")
        for i in range(3):
            Pet.objects.create(**mock_pet_data(User.objects.all().first()))
        # add users (representing likes) to pets
        for pet in Pet.objects.all():
            for user in User.objects.all():
                pet.likes.add(user)

    def test_it_has_correct_fields(self):
        pet = Pet.objects.all().first()
        self.assertIsInstance(pet.name, str)
        self.assertIsInstance(pet.animal, int),
        self.assertIsInstance(pet.age, int)
        self.assertIsInstance(pet.sex, int)
        self.assertIsInstance(pet.eye_color, int)
        self.assertIsInstance(pet.exterior_color, int)
        self.assertIsInstance(pet.weight, int)
        self.assertIsInstance(pet.microchip, str)
        self.assertIsInstance(pet.information, str)
        self.assertIsInstance(pet.status, int)
        self.assertIsInstance(pet.user, User)

    def test_many_to_one_relationship(self):
        pets = Pet.objects.all()
        user = User.objects.all().first()
        self.assertEquals(len(pets), user.pet_set.count())
        for pet in pets:
            self.assertIn(pet, user.pet_set.all())

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
    def setUpTestData(cls):
        user = User.objects.create(username="oscar")
        pet = Pet.objects.create(**mock_pet_data(user))
        for _ in range(3):
            Photo.objects.create(
                url="http://myphotourl.com/123",
                pet=pet,
            )

    def test_it_has_correct_fields(self):
        photo = Photo.objects.all().first()
        self.assertIsInstance(photo.url, str),
        self.assertIsInstance(photo.pet, Pet)

    def test_many_to_one_relationship(self):
        photos = Photo.objects.all()
        pet = Pet.objects.all().first()
        self.assertEquals(len(photos), pet.photo_set.count())
        for photo in photos:
            self.assertIn(photo, pet.photo_set.all())


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
