from django.core.mail import send_mail
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserSerializer
from users.permissions import IsOwner
from users.models import User


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if email:
            send_mail(
                "Password reset request",
                "Click the link to reset your password.",
                "no-reply@example.com",
                [email],
            )
            return Response({"message": "Email sent"}, status=200)
        return Response({"error": "Email is required"}, status=400)


class UserDetailView(RetrieveModelMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
