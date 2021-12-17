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
        "microchip": 900123456789000,
        "information": "last seen on 5th",
        "status": Pet.Status.LOST,
        "user": user,
    }
    return fields


# Create your tests here.
class PetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="oscar")
        cls.pet = Pet.objects.create(**mock_pet_fields(user))

    def test_it_has_correct_fields(self):
        self.assertIsInstance(self.pet.name, str)
        self.assertIsInstance(self.pet.animal, int),
        self.assertIsInstance(self.pet.age, int)
        self.assertIsInstance(self.pet.sex, int)
        self.assertIsInstance(self.pet.eye_color, int)
        self.assertIsInstance(self.pet.exterior_color, int)
        self.assertIsInstance(self.pet.weight, int)
        self.assertIsInstance(self.pet.microchip, int)
        self.assertIsInstance(self.pet.information, str)
        self.assertIsInstance(self.pet.status, int)
        self.assertIsInstance(self.pet.user, User)


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
