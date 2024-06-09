from django.db import models
from common.models import CommonModel
from django.contrib.auth import get_user_model

User = get_user_model()



class PetRating(CommonModel):
    level = models.IntegerField(verbose_name='레벨', default=1)
    point = models.IntegerField(verbose_name='포인트', default=0)

    def __str__(self):
        return f'{self.pet.name} - {self.rating_type}'

class Pet(CommonModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pet', verbose_name='사용자 ID')
    point = models.IntegerField(verbose_name='경험치', default=0)
    name = models.CharField(max_length=50, verbose_name='이름')
    hunger_degree = models.IntegerField(default=0, verbose_name='배고픔 정도')
    type = models.CharField(max_length=50, verbose_name='캐릭터 종류')
    random_boxes = models.IntegerField(verbose_name='랜덤 박스 갯수', default=0)
    petrating = models.ForeignKey(PetRating, on_delete=models.CASCADE, related_name='ratings', verbose_name='레이팅 ID')
    def __str__(self):
        return self.name


class Snack(CommonModel):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='snacks', verbose_name='펫 ID')
    type = models.IntegerField(verbose_name='종류')  # 0: 밥, 1: 간식
    item_name = models.CharField(max_length=10, verbose_name='아이템 이름')

    def __str__(self):
        return self.item_name

class Clothes(CommonModel):
    name = models.CharField(max_length=10, verbose_name='아이템 이름')
    image_url = models.CharField(max_length=254, verbose_name='아이템 이미지 URL')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='clothes', verbose_name='펫 ID')

    def __str__(self):
        return self.name

class Background(CommonModel):
    image_url = models.CharField(max_length=254, verbose_name='배경화면')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='backgrounds', verbose_name='펫 ID')

    def __str__(self):
        return f'Background for {self.pet.name}'

class ItemList(CommonModel):
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE, related_name='item_lists', null=True, blank=True, verbose_name='Clothes ID')
    backgrounds = models.ForeignKey(Background, on_delete=models.CASCADE, related_name='item_lists', null=True, blank=True, verbose_name='Backgrounds ID')
    snacks = models.ForeignKey(Snack, on_delete=models.CASCADE, related_name='item_lists', null=True, blank=True, verbose_name='Snacks ID')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='item_lists', verbose_name='펫 ID')

    def __str__(self):
        return f'Item List for {self.pet.name}'