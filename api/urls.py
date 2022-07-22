from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api import views

urlpatterns = [
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("posts", views.PostsView.as_view(), name="posts"),
    path("posts/<str:pk>", views.PostView.as_view(), name="post"),
    path("register", views.RegisterUserView.as_view(), name="register_user"),
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("pets/breeds", views.BreedsListView.as_view(), name="breeds"),
]
