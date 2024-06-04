from django.db import models
from common.models import CommonModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Pet(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets', verbose_name='사용자 ID')
    point = models.IntegerField(verbose_name='경험치', default=0)
    name = models.CharField(max_length=50, verbose_name='이름')
    hunger_degree = models.IntegerField(default=0, verbose_name='배고픔 정도')
    type = models.CharField(max_length=50, verbose_name='캐릭터 종류')
    random_boxs = models.models.IntegerField(_(""))아이템 랜덤으로 나오는 박스 갯수
    



    def __str__(self):
        return self.name


class Pet_rating(CommonModel):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='ratings', verbose_name='사용자 ID')
    rating_type = models. 펫의 레벨이나, 배고픔 정도를 둘중하나선택.
    level = models.IntegerField
    point = model.PositiveIntegerField 
    