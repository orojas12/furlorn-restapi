from typing import Mapping
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    ValidationError,
    CharField,
    StringRelatedField,
)

from api.models import Breed, Pet, Photo, User, Post
from api.validators import PasswordLengthValidator


class PhotoSerializer(ModelSerializer):
    """
    Serializer class for pet photos. This is only used inside PostSerializer
    and is not meant to be directly used by a view.
    """

    class Meta:
        model = Photo
        fields = ["order", "file"]

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PhotoSerializer)
        return data


class PetSerializer(ModelSerializer):
    """
    Serializer class for lost/found pets. Only used inside PostSerializer
    and not meant to be directly used by a view.
    """

    class Meta:
        model = Pet
        fields = [
            "id",
            "name",
            "species",
            "breed",
            "age",
            "sex",
            "eye_colors",
            "coat_colors",
            "weight",
            "microchip",
        ]
        extra_kwargs = {
            "breed": {"required": False, "default": []},
            "eye_colors": {"required": False, "default": []},
            "coat_colors": {"required": False, "default": []},
            "id": {"read_only": True},
        }

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PetSerializer)
        return data


class PostSerializer(ModelSerializer):
    """
    Serializer class for reading/updating a post.
    """

    pet = PetSerializer(read_only=True)
    user = StringRelatedField(read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "description",
            "likes",
            "location_lat",
            "location_long",
            "status",
            "pet",
            "photos",
            "user",
        ]
        extra_kwargs = {"likes": {"read_only": True}}

    def create(self, validated_data):
        raise NotImplementedError(
            "PostSerializer cannot be used to create new posts. Please use CreatePostSerializer."
        )

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, PostSerializer)
        return data


class CreatePostSerializer(ModelSerializer):
    """
    Serializer class for creating a new post.
    """

    pet = PetSerializer()
    photos = PhotoSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = [
            "description",
            "location_lat",
            "location_long",
            "status",
            "pet",
            "photos",
        ]

    def create(self, validated_data):
        pet_data = validated_data.pop("pet")
        breeds = pet_data.pop("breed", [])
        photos = validated_data.pop("photos", [])
        user = self.context.get("user", None)

        pet = Pet.objects.create(**pet_data)
        pet.breed.set(breeds)
        post = Post.objects.create(pet=pet, user=user, **validated_data)
        for photo_data in photos:
            Photo.objects.create(post=post, **photo_data)
        return post

    def update(self, instance, validated_data):
        raise NotImplementedError(
            "CreatePostSerializer cannot be used to update posts. Please use PostSerializer."
        )

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, CreatePostSerializer)
        return data


class UserSerializer(ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    """
    Serializer class for reading and updating users.
    """

    class Meta:
        model = User
        fields = ["username", "nickname", "posts"]

    def create(self, validated_data):
        raise NotImplementedError(
            "UserSerializer cannot be used to create new users. Please use RegisterUserSerializer."
        )

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
        fields = ["username", "password", "nickname"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        raise NotImplementedError(
            "RegisterUserSerializer cannot be used to update users. Please use UserSerializer."
        )

    def validate(self, data):
        if hasattr(self, "initial_data"):
            raise_if_unknown_fields(self.initial_data, RegisterUserSerializer)
        return data


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


class BreedSerializer(ModelSerializer):
    class Meta:
        model = Breed
        fields = ["id", "name", "species"]


def raise_if_unknown_fields(data: Mapping, serializer_cls: ModelSerializer):
    """Raises a ValidationError if data has fields that do not belong in the ModelSerializer class."""
    unknown_fields = set(data.keys()) - set(serializer_cls.Meta.fields)
    if unknown_fields:
        raise ValidationError(f"Invalid field(s): {unknown_fields}")
