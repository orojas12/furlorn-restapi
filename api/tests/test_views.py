from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


def mock_user_data(partial=False, **kwargs):
    user = {
        "username": "oscar",
        "first_name": "oscar",
        "last_name": "rojas",
        "email": "oscar@email.com",
        "password": "apples",
    }
    if partial:
        user = {**kwargs}
    return user


class UserListTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("users")

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = mock_user_data()
        response = self.client.post(self.url, data, format="json")
        user = User.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.email, data["email"])


class UserDetailTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("user", kwargs={"pk": 1})
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
