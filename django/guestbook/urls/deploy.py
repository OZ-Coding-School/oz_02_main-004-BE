from django.urls import path
from ..views.deploy import GuestBookViewdetail, GuestBookView, GuestBookCommentView, GuestBookCommentUpdateView, GuestBookCommentDeleteView, GuestBookCommentCreateView

urlpatterns = [
    path('<str:nickname>/', GuestBookViewdetail.as_view(), name='guestbook-detail'),
    path('', GuestBookView.as_view(), name='guestbook-list'),
    path('comments/<int:user_id>/', GuestBookCommentView.as_view(), name='guestbook-comment-list'),
    path('comments/a-create/', GuestBookCommentCreateView.as_view(), name='guestbook-comment-create'),
    path('comments/update/', GuestBookCommentUpdateView.as_view(), name='guestbook-comment-update'),
    path('comments/delete/', GuestBookCommentDeleteView.as_view(), name='guestbook-comment-delete'),
]