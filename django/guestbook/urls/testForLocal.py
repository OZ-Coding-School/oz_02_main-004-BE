from django.urls import path
from ..views.testForLocal import *

urlpatterns = [
#     path('<str:nickname>/', GuestBookViewdetail.as_view(), name='guestbook-detail'),
    path('a-test/<str:nickname>/', GuestBookTestView.as_view(), name='guestbook-list'),
    path('comments/a-test/', GuestBookCommentTestView.as_view(), name='guestbook-comment-list-test'),
    path('comments/update/<int:comment_id>/', GuestBookCommentUpdateTestView.as_view(), name='guestbook-comment-update-test'),
    path('comments/delete/<int:comment_id>/', GuestBookCommentDeleteTestView.as_view(), name='guestbook-comment-delete-test'),
]