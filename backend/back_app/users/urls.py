from django.urls import path
from users.views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserRegistrationView,
    UserRetrieveUpdateView,
    UserRetrieveView,
)

urlpatterns = [
    path("info/", UserRetrieveView.as_view(), name="user-retrieve"),
    path("reset-password/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "reset-password-confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="reset-password-confirm",
    ),
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("profile/<uuid:id>/", UserRetrieveUpdateView.as_view(), name="user-retrieve"),
]
