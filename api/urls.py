from django.urls import include, path

from knox import views as knox_views
from api import views

urlpatterns = [
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("posts", views.PostsView.as_view(), name="posts"),
    path("posts/<str:pk>", views.PostView.as_view(), name="post"),
    path("register", views.RegisterUserView.as_view(), name="register_user"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", knox_views.LogoutView.as_view(), name="logout"),
    path("logoutall", knox_views.LogoutAllView.as_view(), name="logout_all"),
    path("pets/breeds", views.BreedsListView.as_view(), name="breeds"),
]
