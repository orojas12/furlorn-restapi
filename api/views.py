import boto3
from django.http.response import Http404
from django.contrib.auth.models import User
from rest_framework import generics, views
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


class PetPhotoList(views.APIView):
    def get_photo_ids(self, pet_id):
        # get photo ids from db
        return ["id1", "id2", "id3"]

    def get_photo_urls(self, keys):
        # get pre-signed object urls from s3 using keys
        return ["url1", "url2"]

    def get(self, request, pk):
        try:
            ids = self.get_photo_ids
            urls = self.get_photo_urls(ids)
        except Photo.DoesNotExist:
            raise Http404
        # except aws error
        return Response(urls)

    def post(self, request):
        pass
