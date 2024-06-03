from django.urls import path
from posts import views

urlpatterns = [
    path("list", views.PostList.as_view()),
    path("music/<int:post_id>", views.Spotify.as_view()),
    # path("myinfo", views.MyInfo.as_view()),
    # path("<int:member_id>", views.UserDetail.as_view()),
]
