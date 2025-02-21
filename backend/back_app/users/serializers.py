from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from rest_framework import serializers
from users.models import User


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "extra_fields", "is_staff", "is_superuser"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_superuser:
            self.fields.pop("is_staff", None)
            self.fields.pop("is_superuser", None)
            self.fields.pop("extra_fields", None)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value

    def send_reset_email(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = (
            f"{settings.URL_NGROK_HOST}/users/reset-password-confirm/{uid}/{token}/"
        )
        send_mail(
            subject="Password Reset Request",
            message=f"Use the link to reset your password: {reset_url}",
            from_email=None,
            recipient_list=[email],
        )
        return reset_url


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uidb64 = self.context.get("uidb64")
        token = self.context.get("token")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user")

        if not default_token_generator.check_token(self.user, token):
            raise serializers.ValidationError("Invalid or expired token")
        return attrs

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
