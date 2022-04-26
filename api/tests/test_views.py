import json
from unittest.mock import patch

from api.models import Animal, Pet, User, Post, Breed
from api.tests.fake_data import (
    FakeUser,
    FakePet,
    FakePost,
    fake_image_file,
)
from api.tests.exceptions import TestException
from api.views import PostView, PostsView, UserView, RegisterUserView
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, force_authenticate


class RegisterUserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("register_user")
        cls.factory = APIRequestFactory()

    def test_post_201_response(self):
        data = FakeUser().data
        request = self.factory.post(self.url, data, format="json")
        response = RegisterUserView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_post_400_response(self):
        data = FakeUser().exclude(["password"])
        request = self.factory.post(self.url, data, format="json")
        response = RegisterUserView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.RegisterUserSerializer.save")
    def test_post_500_response(self, mock_save):
        mock_save.side_effect = TestException()
        data = FakeUser().data
        request = self.factory.post(self.url, data, format="json")
        response = RegisterUserView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)


class UserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.user = User.objects.create_user(**FakeUser().data)
        cls.user2 = User.objects.create_user(**FakeUser().data)
        cls.kwargs = {"username": cls.user.username}
        cls.url = reverse("user", kwargs=cls.kwargs)

    def test_get_200_response(self):
        request = self.factory.get(self.url)
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_get_404_response(self):
        request = self.factory.get(self.url)
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, username=0)  # non-existing username
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_200_response(self):
        data = FakeUser().exclude(["password"])
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_403_response(self):
        data = FakeUser().exclude(["password"])
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, self.user2)
        response = UserView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_404_response(self):
        data = FakeUser().exclude(["password"])
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, username=0)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_400_response(self):
        data = FakeUser().exclude(["email"])
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.UserSerializer.save")
    def test_put_500_response(self, mock_save):
        mock_save.side_effect = TestException()
        data = FakeUser().exclude(["password"])
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_delete_204_response(self):
        request = self.factory.delete(self.url)
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_404_response(self):
        request = self.factory.delete(self.url)
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, username=0)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.User.delete")
    def test_delete_500_response(self, mock_delete):
        mock_delete.side_effect = TestException()
        request = self.factory.delete(self.url)
        force_authenticate(request, self.user)
        response = UserView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)


class PostsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(**FakeUser().data)
        cls.breed = Breed.objects.create(name="American Shorthair", animal=Animal.CAT)
        cls.pet = Pet.objects.create(**FakePet().data)
        cls.pet.breed.set([cls.breed])
        for _ in range(3):
            Post.objects.create(pet=cls.pet, user=cls.user, **FakePost().data)

        cls.url = reverse("posts")
        cls.factory = APIRequestFactory()

    def test_get_200_response(self):
        request = self.factory.get(self.url)
        response = PostsView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), len(Post.objects.all()))

    def test_post_201_response(self):
        data = FakePost().data
        data["pet"] = json.dumps(FakePet().data)
        data["photos"] = [
            fake_image_file(),
            fake_image_file(),
            fake_image_file(),
        ]
        request = self.factory.post(self.url, data)
        force_authenticate(request, self.user)
        response = PostsView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_post_400_response(self):
        invalid_data = FakePost().data
        invalid_data["photos"] = [
            fake_image_file(),
            fake_image_file(),
            fake_image_file(),
        ]
        request = self.factory.post(self.url, data=invalid_data)
        force_authenticate(request, self.user)
        response = PostsView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    @patch("api.views.CreatePostSerializer.save")
    def test_post_500_response(self, mock_save):
        mock_save.side_effect = TestException()
        data = FakePost().data
        data["pet"] = json.dumps(FakePet().data)
        data["photos"] = [
            fake_image_file(),
            fake_image_file(),
            fake_image_file(),
        ]
        request = self.factory.post(self.url, data)
        force_authenticate(request, self.user)
        response = PostsView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)


class PostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(**FakeUser().data)
        cls.pet = Pet.objects.create(**FakePet().data)
        cls.post = Post.objects.create(user=cls.user, pet=cls.pet, **FakePost().data)
        cls.kwargs = {"pk": cls.post.id}
        cls.url = reverse("post", kwargs=cls.kwargs)
        cls.factory = APIRequestFactory()

    def test_get_200_response(self):
        request = self.factory.get(self.url)
        response = PostView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_get_404_response(self):
        request = self.factory.get(self.url)
        response = PostView.as_view()(request, pk=-1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_put_200_response(self):
        new_description = "new description"
        data = FakePost(description=new_description).data
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, self.user)
        response = PostView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], new_description)

    def test_put_404_response(self):
        data = FakePost().data
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, self.user)
        response = PostView.as_view()(request, pk=-1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)

    def test_delete_204_response(self):
        request = self.factory.delete(self.url)
        force_authenticate(request, self.user)
        response = PostView.as_view()(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_404_response(self):
        request = self.factory.delete(self.url)
        force_authenticate(request, self.user)
        response = PostView.as_view()(request, pk=-1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.data, dict)
        self.assertNotEqual(len(response.data), 0)


class LoginUserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_data = FakeUser().data
        cls.user_password = user_data["password"]
        cls.user = User.objects.create_user(**user_data)
        cls.client = APIClient(enforce_csrf_checks=True)
        cls.url = reverse("login_user")

    def test_login(self):
        "Test that login is successful and csrf and session cookies are set correctly."
        response = self.client.post(
            self.url,
            data={
                "username": self.user.username,
                "password": self.user_password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.cookies), 2)
        self.assertIn("csrftoken", response.cookies)
        self.assertIn("sessionid", response.cookies)


class LogoutUserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_data = FakeUser().data
        cls.user_password = user_data["password"]
        cls.user = User.objects.create_user(**user_data)
        cls.client = APIClient(enforce_csrf_checks=True)
        cls.url = reverse("logout_user")

    def test_logout(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
