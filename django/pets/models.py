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
    
"""
bigint	id		테이블 ID	Primary Key	간식 정보 관리
int	type		종류(0:밥, 1:간식)	Not Null	
varchar(10)	item_name		아이템 이름	Not Null	
datetime(6)	created_at		생성 시간	Not Null	
datetime(6)	updated_at		수정 시간	Not Null	
bigint	pet_id		pet ID	Foreign Key	pets 테이블과의 관계 설정
"""
class Snacks(CommonModel):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='snacks', verbose_name='사용자 ID')
    type = models.CharField(max_length=50, verbose_name='캐릭터 종류')
    item_name = models.CharField(max_length=10)
    
