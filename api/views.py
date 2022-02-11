from uuid import uuid4
import boto3
from django.http.response import Http404
from rest_framework import generics, status, views
from rest_framework.response import Response

from api.models import Pet, Photo, User
from api.serializers import UserSerializer, PetSerializer


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PetList(generics.ListCreateAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer


class PetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
