from django.urls import path
from .views import GuestBookView, GuestBookCommentView, GuestBookViewdetail

urlpatterns = [
    path('<str:nickname>/', GuestBookViewdetail.as_view(), name='guestbook-detail'),
    path('', GuestBookView.as_view(), name='guestbook-list'),
    path('<int:user_id>/comments/', GuestBookCommentView.as_view(), name='guestbook-comment-list'),
]