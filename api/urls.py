from django.urls import path

from api import views

urlpatterns = [
    path("users/", views.UserList.as_view(), name="user-list"),
    path("users/<str:pk>/", views.UserDetail.as_view(), name="user-detail"),
    path("pets/", views.PetList.as_view(), name="pet-list"),
    path("pets/<int:pk>/", views.PetDetail.as_view(), name="pet-detail"),
]
