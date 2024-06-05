from django.urls import path
from posts import views

urlpatterns = [
    path("list", views.PostList.as_view(), name="post-list"),
    path("<int:user_id>", views.PostsByUser.as_view(), name="post-by-user"),
    path("todo/<int:post_id>", views.ToDoView.as_view(), name="todo-create-list"),
    path("todo/<int:post_id>/<int:todo_id>", views.ToDoEdit.as_view(), name="todo-edit"),
    path("music/<int:post_id>", views.Spotify.as_view(), name="spotify-api"),
    path("timer/<int:post_id>", views.TimerView.as_view(), name="timer-api"),
]
