from django.db import models
from common.models import CommonModel
from django.contrib.auth import get_user_model
import random

User = get_user_model()


# Accessory model
class Accessory(CommonModel):
    item_name = models.CharField(max_length=100, verbose_name="아이템 이름")
    image = models.ImageField(upload_to="accessories/", verbose_name="아이템 이미지")

    def __str__(self):
        return f"{self.item_name}"


# Background model
class Background(CommonModel):
    item_name = models.CharField(max_length=100, verbose_name="아이템 이름")
    image = models.ImageField(upload_to="backgrounds/", verbose_name="아이템 이미지")

    @staticmethod
    def get_default_background():
        background, created = Background.objects.get_or_create(item_name="봄")
        return background

    def __str__(self):
        return f"{self.item_name}"


# PetCollection model
class PetCollection(CommonModel):
    pet_name = models.CharField(max_length=100, verbose_name="펫 이름")
    image = models.ImageField(upload_to="pet_collections/", verbose_name="펫 이미지")

    @staticmethod
    def get_default_pet():
        pet, created = PetCollection.objects.get_or_create(pet_name="수상한 알")
        return pet

    def __str__(self):
        return f"{self.pet_name}"


# PetRating model
class PetRating(CommonModel):
    level = models.IntegerField(verbose_name="레벨", default=1)
    point = models.IntegerField(verbose_name="포인트", default=0)

    def __str__(self):
        return f"{self.level} - {self.point}"


# Pet model
class Pet(CommonModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="pet", verbose_name="사용자 ID"
    )
    point = models.IntegerField(verbose_name="경험치", default=0)
    hunger_degree = models.DateTimeField(
        auto_now_add=True, verbose_name="최근 식사 시간"
    )  # 최근 밥이나 간식 준 시간
    random_boxes = models.PositiveIntegerField(verbose_name="랜덤 박스 갯수", default=0)
    pet_rating = models.ForeignKey(
        PetRating,
        on_delete=models.CASCADE,
        related_name="pets",
        verbose_name="레이팅 ID",
    )
    primary_accessory = models.ForeignKey(
        Accessory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_accessory_pets",
        verbose_name="대표 악세사리 아이템",
    )
    primary_background = models.ForeignKey(
        Background,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_background_pets",
        verbose_name="대표 배경 아이템",
    )
    primary_pet = models.ForeignKey(
        PetCollection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_pet_pets",
        verbose_name="대표 펫 아이템",
    )
    streak = models.PositiveIntegerField(default=0)

    def open_random_boxes(self):
        if self.random_boxes == 0:
            raise ValueError("No random boxes available")

        accessories = list(Accessory.objects.all())
        backgrounds = list(Background.objects.all())
        items = accessories + backgrounds

        if not items:
            raise ValueError("No accesstory and background object available")

        randomly_chosen_item = random.choice(items)

        # create or get closet instance
        closet, created = Closet.objects.get_or_create(pet=self)

        # check if the chosen item is an instance of Accessory
        if isinstance(randomly_chosen_item, Accessory):
            closet.accessories.add(randomly_chosen_item)
        elif isinstance(randomly_chosen_item, Background):
            closet.backgrounds.add(randomly_chosen_item)

        # update random_boxes
        self.random_boxes -= 1
        self.save()

    def __str__(self):
        return f"{self.user.email}의 펫"


# Closet model
class Closet(CommonModel):
    pet = models.ForeignKey(
        Pet, on_delete=models.CASCADE, related_name="closets", verbose_name="펫 ID"
    )
    accessories = models.ManyToManyField(
        Accessory, blank=True, related_name="closets", verbose_name="악세사리"
    )
    backgrounds = models.ManyToManyField(
        Background, blank=True, related_name="closets", verbose_name="배경화면"
    )
    pet_collections = models.ManyToManyField(
        PetCollection, blank=True, related_name="closets", verbose_name="펫도감"
    )

    def __str__(self):
        return f"{self.pet.user.email}의 옷장"


# SnackType model
class SnackType(CommonModel):
    SNACK_TYPES = (
        ("rice", "밥"),  # ('DB에 저장될 값', '사용자에게 보여질 값')
        ("snack", "간식"),
    )

    name = models.CharField(max_length=10, choices=SNACK_TYPES, verbose_name="이름")
    experience_points = models.IntegerField(verbose_name="경험치", default=0)

    def __str__(self):
        return f"{self.name} - {self.experience_points}"


# Snack model
class Snack(CommonModel):
    pet = models.ForeignKey(
        Pet, on_delete=models.CASCADE, related_name="snacks", verbose_name="펫 ID"
    )
    snack_type = models.ForeignKey(
        SnackType, on_delete=models.CASCADE, related_name="snacks", verbose_name="종류"
    )  # 밥, 간식 구분

    def __str__(self):
        return f"{self.pet.user.email}의 {self.snack_type.name}"
