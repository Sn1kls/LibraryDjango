from django.urls import path
from users.views import UserDetailView, PasswordResetView

urlpatterns = [
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
]
