from django.urls import path
from .views import GuestBookView, GuestBookCommentView, GuestBookViewdetail,GuestBookCommentDeleteView , GuestBookCommentUpdateView

urlpatterns = [
    # same
    path('<str:nickname>/', GuestBookViewdetail.as_view(), name='guestbook-detail'),
    # ''
    path('test/<str:nickname>/', GuestBookView.as_view(), name='guestbook-list'),
    path('comments/<int:user_id>/', GuestBookCommentView.as_view(), name='guestbook-comment-list'),
    path('comments/update/<int:comment_id>/', GuestBookCommentUpdateView.as_view(), name='guestbook-comment-update'),
    path('comments/delete/<int:comment_id>/', GuestBookCommentDeleteView.as_view(), name='guestbook-comment-delete'),
]