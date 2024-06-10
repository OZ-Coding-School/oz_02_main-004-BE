from django.urls import path
from .views import GuestBookView, GuestBookCommentView

urlpatterns = [
    path('', GuestBookView.as_view(), name='guestbook-list'),
    path('<int:guestbook_id>/comments/', GuestBookCommentView.as_view(), name='guestbook-comment-list'),
]