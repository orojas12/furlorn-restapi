from django.urls import path
from django.contrib.auth import views as auth_views

from api import views

urlpatterns = [
    path("users/<str:username>", views.UserView.as_view(), name="user"),
    path("posts", views.PostsView.as_view(), name="posts"),
    path("posts/<str:pk>", views.PostView.as_view(), name="post"),
    path("register", views.RegisterUserView.as_view(), name="register_user"),
    path("login", views.LoginUserView.as_view(), name="login_user"),
    path("logout", views.LogoutUserView.as_view(), name="logout_user"),
]
