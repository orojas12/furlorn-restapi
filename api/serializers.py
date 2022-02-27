from typing import Mapping
from rest_framework import serializers

from api.models import Pet, PetLastKnownLocation, Photo, User


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer class for Photo model.
    """

    class Meta:
        model = Photo
        fields = ["order", "file"]

    order = serializers.IntegerField()
    file = serializers.ImageField()

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PhotoSerializer)
        return data


class UserLikeSerializer(serializers.ModelSerializer):
    """
    Serializer class for UserLike model.
    """

    class Meta:
        model = User
        fields = ["id", "username"]

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, UserLikeSerializer)
        return data


class PetLastKnownLocationSerializer(serializers.ModelSerializer):
    """
    Serializer class for PetLastKnownLocation model.
    """

    class Meta:
        model = PetLastKnownLocation
        fields = ["latitude", "longitude"]

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PetLastKnownLocationSerializer)
        return data


class PetSerializer(serializers.ModelSerializer):
    """
    Serializer class for Pet model.
    """

    last_known_location = PetLastKnownLocationSerializer()
    photos = PhotoSerializer(many=True, required=False)
    likes = UserLikeSerializer(many=True, read_only=True)

    class Meta:
        model = Pet
        fields = [
            "id",
            "name",
            "animal",
            "breed",
            "age",
            "sex",
            "eye_color",
            "color",
            "weight",
            "microchip",
            "information",
            "status",
            "user",
            "likes",
            "photos",
            "last_known_location",
        ]
        extra_kwargs = {"breed": {"required": False, "default": None}}

    def create(self, validated_data):
        breed_list = validated_data.pop("breed", [])
        location_data = validated_data.pop("last_known_location")
        photos = validated_data.pop("photos", [])
        pet = Pet.objects.create(**validated_data)

        if breed_list:
            for breed_id in breed_list:
                pet.breed.add(breed_id)

        PetLastKnownLocation.objects.create(pet=pet, **location_data)

        for photo_data in photos:
            Photo.objects.create(pet=pet, **photo_data)

        return pet

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PetSerializer)
        return data


class UserSerializer(serializers.ModelSerializer):
    pets = PetSerializer(many=True, read_only=True)
    """
    Serializer class for User model.
    """

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password", "email", "pets"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True, "write_only": True},
        }

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, UserSerializer)
        return data


def raise_if_unknown_fields(data: Mapping, serializer_cls: serializers.ModelSerializer):
    """Raises a ValidationError if data has fields that do not belong in the ModelSerializer class."""
    unknown_fields = set(data.keys()) - set(serializer_cls.Meta.fields)
    if unknown_fields:
        raise serializers.ValidationError(f"Invalid field(s): {unknown_fields}")
