from typing import Mapping
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    ValidationError,
    IntegerField,
    ImageField,
    CharField,
)

from api.models import Pet, PetLastKnownLocation, Photo, User
from api.validators import PasswordLengthValidator


class PhotoSerializer(ModelSerializer):
    """
    Serializer class for pet photos. This is only used inside PetSerializer
    and is not meant to be used by itself.
    """

    class Meta:
        model = Photo
        fields = ["order", "file"]

    order = IntegerField()
    file = ImageField()

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PhotoSerializer)
        return data


class UserLikeSerializer(ModelSerializer):
    """
    Serializer class for adding a like to a post.
    """

    class Meta:
        model = User
        fields = ["id", "username"]

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, UserLikeSerializer)
        return data


class PetLastKnownLocationSerializer(ModelSerializer):
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


class PetSerializer(ModelSerializer):
    """
    Serializer class for lost/found pets.
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
        extra_kwargs = {"breed": {"required": False, "default": []}}

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

    def update(self, instance, validated_data):
        """
        This method allows for updating nested objects which cannot
        be done with the default ModelSerializer update() method.
        """

        # Prevent 'user' from being updated
        validated_data.pop("user", None)

        location_data = validated_data.pop("last_known_location", None)
        if location_data:
            location = PetLastKnownLocation.objects.filter(pet=instance).first()
            location.latitude = location_data.get("latitude", location.latitude)
            location.longitude = location_data.get("longitude", location.longitude)
        return super().update(instance, validated_data)

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PetSerializer)
        return data


class UserSerializer(ModelSerializer):
    pets = PetSerializer(many=True, read_only=True)
    """
    Serializer class for reading and updating users.
    """

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "pets"]

    def create(self, validated_data):
        raise NotImplementedError(
            "UserSerializer cannot be used to create new users. Please use RegisterUserSerializer."
        )

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, UserSerializer)
        return data


class RegisterUserSerializer(ModelSerializer):
    """Serializer class for registering new users."""

    password = CharField(
        max_length=128,
        validators=[PasswordLengthValidator()],
        write_only=True,
    )

    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name"]
        extra_kwargs = {
            "email": {"write_only": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        raise NotImplementedError(
            "RegisterUserSerializer cannot be used to update users. Please use UserSerializer."
        )


class ChangePasswordSerializer(Serializer):
    """Serializer class for changing a user's password."""

    old_password = CharField(max_length=128)
    new_password = CharField(
        max_length=128,
        validators=[PasswordLengthValidator()],
    )

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

    def validate(self, data):
        # Verify old password before updating.
        if self.instance.check_password(data["old_password"]):
            return data
        else:
            raise ValidationError("Incorrect password.")


def raise_if_unknown_fields(data: Mapping, serializer_cls: ModelSerializer):
    """Raises a ValidationError if data has fields that do not belong in the ModelSerializer class."""
    unknown_fields = set(data.keys()) - set(serializer_cls.Meta.fields)
    if unknown_fields:
        raise ValidationError(f"Invalid field(s): {unknown_fields}")
