from rest_framework import serializers
from django.contrib.auth.models import User

from api.models import Pet, Photo


class UserProfileSerializer(serializers.ModelSerializer):
    pets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "pets"]


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password", "email"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = "__all__"


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"
