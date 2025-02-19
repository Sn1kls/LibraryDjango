import uuid

from core.settings import URL_NGROK_HOST
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User
from users.permissions import IsOwnerOrAdmin
from users.serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{URL_NGROK_HOST}/users/reset-password-confirm/{uid}/{token}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Use the link to reset your password: {reset_url}",
            from_email=None,
            recipient_list=[email],
        )

        return Response(
            {"detail": "Password reset link sent."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, uidb64, token, *args, **kwargs):

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Password has been reset."}, status=status.HTTP_200_OK
        )


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "User created successfully."}, status=status.HTTP_201_CREATED
        )


class UserRetrieveUpdateView(
    generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_object(self):
        user_id = self.kwargs.get(self.lookup_url_kwarg)

        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    @swagger_auto_schema(
        operation_description="Retrieve user profile by ID",
        responses={200: UserSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update user profile by ID",
        request_body=UserSerializer,
        responses={200: UserSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update user profile by ID",
        request_body=UserSerializer,
        responses={200: UserSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete user profile by ID",
        responses={204: "User deleted"},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
