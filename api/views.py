from rest_framework import generics

from api.models import User, Pet
from api.serializers import UserSerializer, PetSerializer

# Create your views here.
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
