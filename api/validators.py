from rest_framework.serializers import ValidationError


class PasswordLengthValidator:
    """Validates that a user password is at an acceptable length."""

    def __init__(self, min_length=8, max_length=128):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        length = len(value)
        if length < self.min_length or length > self.max_length:
            message = (
                f"Password must be {self.min_length}-{self.max_length} characters long."
            )
            raise ValidationError(message)
