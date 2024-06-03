from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Pet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets', verbose_name='사용자 ID')
    point = models.IntegerField(verbose_name='경험치', default=0)
    level = models.IntegerField(verbose_name='레벨', default=1)
    name = models.CharField(max_length=50, verbose_name='이름')
    status = models.CharField(max_length=50, verbose_name='상태')
    type = models.CharField(max_length=50, verbose_name='캐릭터 종류')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')

    def __str__(self):
        return self.name
