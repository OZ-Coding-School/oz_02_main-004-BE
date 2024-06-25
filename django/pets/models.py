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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pet', verbose_name='사용자 ID')
    point = models.IntegerField(verbose_name='경험치', default=0)
    hunger_degree = models.DateTimeField(null=True, blank=True, verbose_name='최근 식사 시간')  # 최근 밥이나 간식 준 시간
    random_boxes = models.PositiveIntegerField(verbose_name='랜덤 박스 갯수', default=0)
    pet_rating = models.ForeignKey(PetRating, on_delete=models.CASCADE, related_name='pets', verbose_name='레이팅 ID',)
    primary_accessory = models.ForeignKey(Accessory, null=True, blank=True, on_delete=models.SET_NULL, related_name='primary_accessory_pets', verbose_name='대표 악세사리 아이템',)
    primary_background = models.ForeignKey(Background, null=True, blank=True, on_delete=models.SET_NULL, related_name='primary_background_pets', verbose_name='대표 배경 아이템',)
    primary_pet = models.ForeignKey(PetCollection, null=True, blank=True, on_delete=models.SET_NULL, related_name='primary_pet_pets', verbose_name='대표 펫 아이템',)
    active_pet = models.ForeignKey(PetCollection, null=True, blank=True, on_delete=models.SET_NULL, related_name='active_pet_pets', verbose_name='키우는 펫 아이템',)
    streak = models.PositiveIntegerField(default=0)
    last_snack_date = models.DateField(null=True, blank=True, verbose_name='최근 간식(밥) 날짜')
# In the Pet model

    def open_random_boxes(self):
        if self.random_boxes == 0:
            raise ValueError('No random boxes available')

        # Get all possible items
        accessories = list(Accessory.objects.all())
        backgrounds = list(Background.objects.all())
        snacks = list(SnackType.objects.filter(name='snack'))

        # Get the user's current items
        closet, created = Closet.objects.get_or_create(pet=self)
        user_accessories = closet.accessories.all()
        user_backgrounds = closet.backgrounds.all()

        # Determine which items the user does not have
        available_accessories = [item for item in accessories if item not in user_accessories]
        available_backgrounds = [item for item in backgrounds if item not in user_backgrounds]

        # Combine available items, ensuring no duplicates
        available_items = available_accessories + available_backgrounds + snacks

        # If the user has all accessories and backgrounds, only provide snacks
        if not available_accessories and not available_backgrounds:
            available_items = snacks

        randomly_chosen_item = random.choice(available_items)

        output_item = None

        if isinstance(randomly_chosen_item, SnackType):
            # Create or get snack instance
            snack, created = Snack.objects.get_or_create(
                pet=self, snack_type=randomly_chosen_item
            )
            snack.quantity += 1
            snack.save()
            output_item = {'type': 'snack', 'name': snack.snack_type.name, 'quantity': snack.quantity, 'image': snack.snack_type.image.url if snack.snack_type.image else ''}
        else:
            # Add the chosen item to the user's closet
            if isinstance(randomly_chosen_item, Accessory):
                closet.accessories.add(randomly_chosen_item)
                output_item = {'type': 'accessory', 'name': randomly_chosen_item.item_name, 'image': randomly_chosen_item.image.url if randomly_chosen_item.image else ''}
            elif isinstance(randomly_chosen_item, Background):
                closet.backgrounds.add(randomly_chosen_item)
                output_item = {'type': 'background', 'name': randomly_chosen_item.item_name, 'image': randomly_chosen_item.image.url if randomly_chosen_item.image else ''}

        # Update random_boxes
        self.random_boxes -= 1
        self.save()

        return output_item


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
        ('rice', '밥'),  # ('DB에 저장될 값', '사용자에게 보여질 값')
        ('snack', '간식'),
    )


    name = models.CharField(max_length=10, choices=SNACK_TYPES, verbose_name='이름')
    experience_points = models.IntegerField(verbose_name='경험치', default=0)
    image = models.ImageField(upload_to='snacktypes/', verbose_name='음식 이미지', null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.experience_points}"


# Snack model
class Snack(CommonModel):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='snacks', verbose_name='펫 ID')
    snack_type = models.ForeignKey(SnackType, on_delete=models.CASCADE, related_name='snacks', verbose_name='종류')  # 밥, 간식 구분
    quantity = models.IntegerField(verbose_name='개수', default=0)

    def __str__(self):
        return f'{self.pet.user.email}의 {self.snack_type.name} ({self.quantity}개)'

