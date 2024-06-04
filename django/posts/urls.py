from django.urls import path
from posts import views

urlpatterns = [
    path("list", views.PostList.as_view()),
    path("<int:user_id>", views.PostsByUser.as_view()),
    path("music/<int:post_id>", views.Spotify.as_view()),
]
