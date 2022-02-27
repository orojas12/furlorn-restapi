from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import status, views
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from api.models import Pet, User
from api.serializers import PetSerializer, UserSerializer
from api.parsers import MultiPartJSONParser


class UserList(views.APIView):
    """
    A view class for creating new users.
    """

    parser_classes = [JSONParser]

    def post(self, request, format="json"):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return response_400(serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            print(e)
            return response_500()
        return response_201(serializer.data)


class UserDetail(views.APIView):
    """
    A view class for reading/updating user data, and for deleting users.
    """

    parser_classes = [JSONParser]

    def get(self, request, pk=None):
        user = get_obj(User, pk)
        if user is None:
            return response_404()
        serializer = UserSerializer(user)
        return response_200(serializer.data)

    def patch(self, request, pk=None):
        user = get_obj(User, pk)
        if user is None:
            return response_404()

        serializer = UserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return response_400(serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            print(e)
            return response_500()
        return response_200(serializer.data)

    def put(self, request, pk=None):
        user = get_obj(User, pk)
        if user is None:
            return response_404()

        serializer = UserSerializer(user, data=request.data)
        if not serializer.is_valid():
            return response_400(serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            print(e)
            return response_500()
        return response_200(serializer.data)

    def delete(self, request, pk=None):
        user = get_obj(User, pk)
        if user is None:
            return response_404()

        try:
            user.delete()
            return response_204()
        except Exception as e:
            print(e)
            return response_500()


class PetList(views.APIView):
    """A View class for searching for lost and found pets and creating new posts."""

    parser_classes = [MultiPartJSONParser]

    def get(self, request):
        pets = Pet.objects.all()
        serializer = PetSerializer(pets, many=True)
        return response_200(serializer.data)

    def post(self, request):
        data = request.data
        for i, file in enumerate(data["photos"]):
            data["photos"][i] = {"order": i, "file": file}
        serializer = PetSerializer(data=request.data)
        if not serializer.is_valid():
            return response_400(serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            print(e)
            return response_500()
        return response_201(serializer.data)


class PetDetail(views.APIView):
    pass


def response_200(data):
    return Response(data=data, status=status.HTTP_200_OK)


def response_201(data):
    return Response(data=data, status=status.HTTP_201_CREATED)


def response_204():
    return Response(status=status.HTTP_204_NO_CONTENT)


def response_400(data):
    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


def response_404():
    return Response(
        data={"detail": "Object not found."}, status=status.HTTP_404_NOT_FOUND
    )


def response_500():
    return Response(
        data={"detail": "Server error. Please try again later."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def get_obj(model: models.Model, pk):
    try:
        return model.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return None


def delete_obj(model: models.Model, pk):
    try:
        return model.objects.get(pk=pk).delete()
    except ObjectDoesNotExist:
        return None
