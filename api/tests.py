from django.test import TestCase
from django.contrib.auth.models import User

from api.models import Pet, Animal, Photo, Sex, Breed


def mock_pet_fields(user):
    fields = {
        "name": "Yuna",
        "animal": Animal.CAT,
        "age": 2,
        "sex": Sex.FEMALE,
        "eye_color": Pet.Color.YELLOW,
        "exterior_color": Pet.Color.BROWN,
        "weight": 8,
        "microchip": "900123456789000",
        "information": "last seen on 5th",
        "status": Pet.Status.LOST,
        "user": user,
    }
    return fields


# Create your tests here.
class PetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create 3 users and 3 pets (pet.user does not matter here)
        for i in range(3):
            User.objects.create(username=f"oscar{i}")
        for i in range(3):
            Pet.objects.create(**mock_pet_fields(User.objects.all().first()))
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
        cls.breed = Breed.objects.create(
            name="American Shorthair",
            animal=Animal.CAT,
        )

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.breed.name, str)
        self.assertIsInstance(self.breed.animal, int)


class PhotoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="oscar")
        cls.pet = Pet.objects.create(**mock_pet_fields(user))
        cls.photos = [
            Photo.objects.create(
                url="http://myphotourl.com/123",
                pet=cls.pet,
            )
            for _ in range(3)
        ]

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.photos[0].url, str),
        self.assertIsInstance(self.photos[0].pet, Pet)

    def test_many_to_one_relationship(self):
        self.assertEquals(len(self.photos), Photo.objects.filter(pet=self.pet).count())
        for photo in self.photos:
            self.assertIn(photo, Photo.objects.filter(pet=self.pet))
