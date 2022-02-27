from unittest.mock import patch

from api.models import Pet, User
from api.tests.fake_data import fake_image_file, fake_pet_data, fake_user_data
from api.views import PetList, UserDetail, UserList
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory


class UserListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("user-list")
        cls.factory = APIRequestFactory()

    def test_post_201_response(self):
        data = fake_user_data()
        request = self.factory.post(self.url, data, format="json")
        response = UserList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_post_400_response(self):
        data = fake_user_data(exclude=["password"])
        request = self.factory.post(self.url, data, format="json")
        response = UserList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.UserSerializer.save")
    def test_post_500_response(self, mock_save):
        mock_save.side_effect = Exception("test exception")
        data = fake_user_data()
        request = self.factory.post(self.url, data, format="json")
        response = UserList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)


class UserDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.user = User.objects.create(**fake_user_data())
        cls.kwargs = {"pk": cls.user.id}
        cls.url = reverse("user-detail", kwargs=cls.kwargs)

    def test_get_200_response(self):
        request = self.factory.get(self.url)
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_get_404_response(self):
        request = self.factory.get(self.url)
        response = UserDetail.as_view()(request, pk=0)  # non-existing pk
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_patch_200_response(self):
        data = {"email": "newemail@email.com"}
        request = self.factory.patch(self.url, data, format="json")
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_patch_404_response(self):
        data = {"user": {"email": "newemail@email.com"}}
        request = self.factory.patch(self.url, data, format="json")
        response = UserDetail.as_view()(request, pk=0)  # non-existing pk
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_patch_400_response(self):
        data = {"user_data": {"email": "newemail@email.com"}}  # invalid key name
        request = self.factory.patch(self.url, data, format="json")
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.UserSerializer.save")
    def test_patch_500_response(self, mock_save):
        mock_save.side_effect = Exception("test exception")
        data = fake_user_data(exclude=["email"])
        request = self.factory.patch(self.url, data, format="json")
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_200_response(self):
        data = fake_user_data(username="updateduser1")
        request = self.factory.put(self.url, data, format="json")
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_404_response(self):
        data = fake_user_data(username="updateduser1")
        request = self.factory.put(self.url, data, format="json")
        response = UserDetail.as_view()(request, pk=0)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_400_response(self):
        data = fake_user_data(exclude=["email"])
        request = self.factory.put(self.url, data, format="json")
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.UserSerializer.save")
    def test_put_500_response(self, mock_save):
        mock_save.side_effect = Exception("test exception")
        data = fake_user_data(username="updateduser1")
        request = self.factory.put(self.url, data, format="json")
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_delete_204_response(self):
        request = self.factory.delete(self.url)
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_404_response(self):
        request = self.factory.delete(self.url)
        response = UserDetail.as_view()(request, pk=0)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.User.delete")
    def test_delete_500_response(self, mock_delete):
        mock_delete.side_effect = Exception("test exception")
        request = self.factory.delete(self.url)
        response = UserDetail.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)


class PetListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**fake_user_data())
        for _ in range(3):
            Pet.objects.create(**fake_pet_data(cls.user))

        cls.url = reverse("pet-list")
        cls.factory = APIRequestFactory()

    def test_get_200_response(self):
        request = self.factory.get(self.url)
        response = PetList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), len(Pet.objects.all()))

    def test_post_201_response(self):
        # TODO: change other tests to use multipart data
        data = fake_pet_data(self.user, serializable=True, format="multipart")
        data["photos"] = [
            fake_image_file(),
            fake_image_file(),
            fake_image_file(),
        ]
        request = self.factory.post(self.url, data)
        response = PetList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_post_400_response(self):
        invalid_data = fake_pet_data(
            self.user,
            serializable=True,
            exclude=["last_known_location"],
            format="multipart",
        )
        invalid_data["photos"] = [
            fake_image_file(),
            fake_image_file(),
            fake_image_file(),
        ]
        request = self.factory.post(self.url, data=invalid_data)
        response = PetList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.PetSerializer.save")
    def test_post_500_response(self, mock_save):
        mock_save.side_effect = Exception("test exception")
        data = fake_pet_data(self.user, serializable=True, format="multipart")
        data["photos"] = [
            fake_image_file(),
            fake_image_file(),
            fake_image_file(),
        ]
        request = self.factory.post(self.url, data)
        response = PetList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)
