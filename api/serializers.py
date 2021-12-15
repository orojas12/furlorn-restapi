from rest_framework import serializers
from django.contrib.auth.models import User

from api.models import Pet, Photo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = "__all__"


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"
