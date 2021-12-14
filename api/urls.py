from django.urls import path

from api import views

urlpatterns = [
    path("users/", views.UserList.as_view()),
    path("users/<str:pk>/", views.UserDetail.as_view()),
    path("pets/", views.PetList.as_view()),
    path("pets/<int:pk>/", views.PetDetail.as_view()),
    path("pets/<int:pk>/photos/", views.PetPhotoList.as_view()),
]
