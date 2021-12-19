from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Pet, Photo
from api.serializers import PetSerializer
from api.tests.mock import mock_pet_data, mock_user_data


class UserListTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("user-list")
        User.objects.create(**mock_user_data())

    def test_list(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)

    def test_create(self):
        data = mock_user_data(username="daniel")
        response = self.client.post(self.url, data, format="json")
        user = User.objects.get(username="daniel")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.email, data["email"])


class UserDetailTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("user-detail", kwargs={"pk": 1})
        User.objects.create(**mock_user_data())

    def test_retrieve(self):
        response = self.client.get(self.url)
        data = response.json()
        user = User.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["username"], user.username)
        self.assertEqual(data["first_name"], user.first_name)
        self.assertEqual(data["last_name"], user.last_name)
        self.assertEqual(data["email"], user.email)

    def test_update(self):
        data = mock_user_data()
        data["first_name"] = "daniel"
        response = self.client.put(self.url, data, format="json")
        user = User.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.email, data["email"])

    def test_update_partial(self):
        partial_data = mock_user_data(partial=True, last_name="padilla")
        response = self.client.patch(self.url, partial_data, format="json")
        user = User.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.last_name, partial_data["last_name"])

    def test_destroy(self):
        response = self.client.delete(self.url)
        users = User.objects.all()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(users), 0)


class PetListTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("pet-list")
        user = User.objects.create(**mock_user_data())
        Pet.objects.create(**mock_pet_data(user=user))

    def test_list(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)

    def test_create(self):
        user_pk = User.objects.get().pk
        pet_data = mock_pet_data(user=user_pk)
        response = self.client.post(self.url, pet_data, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in pet_data:
            if key == "user":
                continue
            self.assertEqual(pet_data[key], data[key])


class PetDetailTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("pet-detail", kwargs={"pk": 1})
        user = User.objects.create(**mock_user_data())
        Pet.objects.create(**mock_pet_data(user=user))

    def test_retrieve(self):
        serializer = PetSerializer(Pet.objects.get())
        pet_data = serializer.data
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in data:
            self.assertEqual(data[key], pet_data[key])

    def test_update(self):
        serializer = PetSerializer(Pet.objects.get())
        data = serializer.data
        data["name"] = "maya"
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_data = response.json()
        for key, value in updated_data.items():
            self.assertEqual(value, data[key])

    def test_update_partial(self):
        data = {"name": "Dakota"}
        response = self.client.patch(self.url, data, format="json")
        pet_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(pet_data["name"], data["name"])

    def test_destroy(self):
        response = self.client.delete(self.url)
        pets = Pet.objects.all()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(pets), 0)


class PetDetailPhotoListTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("pet-detail-photos", kwargs={"pk": 1})
        user = User.objects.create(**mock_user_data())
        pet = Pet.objects.create(**mock_pet_data(user=user))
        for i in range(3):
            Photo.objects.create(url=f"http://url{i}.com", pet=pet)

    def test_list(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)
        for i, obj in enumerate(data):
            self.assertEqual(obj["url"], f"http://url{i}.com")

    def test_create(self):
        pet = Pet.objects.get()
        new_photo = {"url": "http://url4.com", "pet": pet.pk}
        response = self.client.post(self.url, data=new_photo, format="json")
        photos = Photo.objects.filter(pet=pet)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(photos), 4)
        for key, value in new_photo.items():
            self.assertEqual(data[key], value)
