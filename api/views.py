import boto3
from django.http.response import Http404
from django.contrib.auth.models import User
from rest_framework import generics, status, views
from rest_framework.response import Response

from api.models import Pet, Photo
from api.serializers import PhotoSerializer, UserSerializer, PetSerializer

s3 = boto3.resource("s3")
S3_BUCKET = "lostneighborhoodpets.com"

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


class PetDetailPhotoList(views.APIView):
    def get(self, request, pk):
        photos = Photo.objects.filter(pet=pk)
        serializer = PhotoSerializer(photos, many=True)
        return Response(data=serializer.data)

    def post(self, request, pk):
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
