import logging
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from api.models import Breed, User, Post
from api.serializers import (
    BreedSerializer,
    CreatePostSerializer,
    RegisterUserSerializer,
    UserSerializer,
    PostSerializer,
    LoginUserSerializer,
)
from api.parsers import MultiPartJSONParser
from api.permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)


class ProfileView(APIView):
    """
    A view class for reading/updating user data, and for deleting users.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return response_200(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return response_200(serializer.data)
            except Exception as exc:
                logger.exception(exc)
                return response_500()
        else:
            return response_400(serializer.errors)

    def delete(self, request):
        try:
            request.user.delete()
            return response_204()
        except Exception as exc:
            logger.exception(exc)
            return response_500()


class PostsView(APIView):
    """A View class for reading and creating new posts."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartJSONParser]

    def get(self, request):
        posts = Post.objects.select_related("pet", "user").prefetch_related("photos")
        serializer = PostSerializer(posts, many=True)
        return response_200(serializer.data)

    def post(self, request):
        data = request.data
        data["photos"] = [
            {"order": i, "file": file} for i, file in enumerate(data["photos"])
        ]
        serializer = CreatePostSerializer(data=data, context={"user": request.user})

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response_201(serializer.data)
        except ValidationError as exc:
            return response_400(serializer.errors)
        except Exception as exc:
            logger.exception(exc)
            return response_500()


class PostView(APIView):
    """A View class for retrieve/update/delete for a pet."""

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [JSONParser]

    def get(self, request, pk=None):
        try:
            post = (
                Post.objects.select_related("pet").prefetch_related("photos").get(pk=pk)
            )
        except ObjectDoesNotExist:
            return response_404()

        serializer = PostSerializer(post)
        return response_200(serializer.data)

    def put(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return response_404()

        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return response_200(serializer.data)
            except Exception as exc:
                logger.exception(exc)
                return response_500()
        else:
            return response_400(serializer.errors)

    def delete(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return response_404()

        self.check_object_permissions(request, post)
        try:
            post.delete()
            return response_204()
        except Exception as exc:
            logger.exception(exc)
            return response_500()


class RegisterUserView(APIView):
    """A View class for registering new users."""

    parser_classes = [JSONParser]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return response_201(serializer.data)
            except Exception as exc:
                logger.exception(exc)
                return response_500()
        else:
            return response_400(serializer.errors)


class BreedsListView(APIView):
    """A View class for getting a list of all existing breeds."""

    parser_classes = [JSONParser]

    def get(self, request):
        breeds = Breed.objects.all()
        serializer = BreedSerializer(breeds, many=True)
        return response_200(serializer.data)


def response_200(data):
    return Response(data=data, status=status.HTTP_200_OK)


def response_201(data):
    return Response(data=data, status=status.HTTP_201_CREATED)


def response_204():
    return Response(status=status.HTTP_204_NO_CONTENT)


def response_400(data):
    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


def response_403():
    return Response(
        data={"detail": "Username or password is incorrect."},
        status=status.HTTP_403_FORBIDDEN,
    )


def response_404():
    return Response(
        data={"detail": "Object not found."}, status=status.HTTP_404_NOT_FOUND
    )


def response_500():
    return Response(
        data={"detail": "Server error. Please try again later."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
