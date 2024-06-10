from django.db import models
from common.models import CommonModel
from django.contrib.auth import get_user_model

User = get_user_model()

class GuestBook(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guestbooks', verbose_name='사용자 ID')

    def __str__(self):
        return f'{self.user.email} - 방명록'

class GuestBookComment(CommonModel):
    guestbook = models.ForeignKey(GuestBook, on_delete=models.CASCADE, related_name='comments', verbose_name='방명록 ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guestbook_comments', verbose_name='사용자 ID')
    content = models.TextField(verbose_name='내용')

    def __str__(self):
        return f'{self.user.email} - 댓글'
