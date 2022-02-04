from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Pet, PetLastKnownLocation, Photo, UserProfile


class PhotoSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    file = serializers.ImageField()


class UserLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class PetLastKnownLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetLastKnownLocation
        fields = ["latitude", "longitude"]


class PetSerializer(serializers.ModelSerializer):
    last_known_location = PetLastKnownLocationSerializer()
    photos = PhotoSerializer(many=True, required=False)
    likes = UserLikeSerializer(many=True, read_only=True)

    class Meta:
        model = Pet
        fields = "__all__"
        extra_kwargs = {"breed": {"required": False, "default": None}}

    def create(self, validated_data):
        breed_list = validated_data.pop("breed")
        location_data = validated_data.pop("last_known_location")
        photos = validated_data.pop("photos")
        pet = Pet.objects.create(**validated_data)

        if breed_list:
            for breed_id in breed_list:
                pet.breed.add(breed_id)

        PetLastKnownLocation.objects.create(pet=pet, **location_data)

        for photo_data in photos:
            Photo.objects.create(pet=pet, **photo_data)

        return pet


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password", "email"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True, "write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        profile = UserProfile.objects.create(user=user)
        return profile


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    pets = PetSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"
