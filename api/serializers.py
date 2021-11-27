from rest_framework import serializers

from api.models import User, Pet


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = "__all__"
