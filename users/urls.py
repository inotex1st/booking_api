from django.urls import path

from users.views import CurrentUserView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("users/me/", CurrentUserView.as_view(), name="users-me"),
]
