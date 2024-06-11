from django.urls import path
from .views import GuestBookView, GuestBookCommentView, GuestBookViewdetail

urlpatterns = [
    path('<str:nickname>/', GuestBookViewdetail.as_view(), name='guestbook-detail'),
    path('test/<str:nickname>/', GuestBookView.as_view(), name='guestbook-list'),
    path('comments/<int:user_id>/', GuestBookCommentView.as_view(), name='guestbook-comment-list'),
]