# pets/serializers.py
from rest_framework import serializers
from .models import Pet, Accessory, Background, PetCollection, Snack, SnackType, PetRating

class AccessorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessory
        fields = ['item_name', 'image']

class BackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Background
        fields = ['item_name', 'image']

class PetCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetCollection
        fields = ['pet_name', 'image']

class PetratingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetRating
        fields = ['level', 'point']

class PetSerializer(serializers.ModelSerializer):
    primary_accessory = AccessorySerializer()
    primary_background = BackgroundSerializer()
    pet_rating = PetratingSerializer()
    primary_pet = PetCollectionSerializer()
    rice_quantity = serializers.SerializerMethodField()
    snack_quantity = serializers.SerializerMethodField()
    active_pet = PetCollectionSerializer()
    hunger_degree_status = serializers.SerializerMethodField()

    def get_rice_quantity(self, obj):
        rice_type = SnackType.objects.get(name='rice')
        rice_snack = Snack.objects.filter(pet=obj, snack_type=rice_type).first()
        return rice_snack.quantity if rice_snack else 0

    def get_snack_quantity(self, obj):
        snack_type = SnackType.objects.get(name='snack')
        snack_snack = Snack.objects.filter(pet=obj, snack_type=snack_type).first()
        return snack_snack.quantity if snack_snack else 0
    
    def get_hunger_degree_status(self, obj):
        from datetime import datetime, time, timedelta
        from django.utils import timezone

        current_time = timezone.now()
        today_5am = timezone.make_aware(datetime.combine(current_time.date(), time(5, 0)))

        if obj.hunger_degree and obj.hunger_degree >= today_5am:
            return "당신의 펫은 만족스러운 식사를 했습니다!"
        return "당신의 펫은 배고픕니다!"

    
    class Meta:
        model = Pet
        fields = [
            'user', 'point', 'hunger_degree', 'random_boxes', 'pet_rating', 'primary_accessory',
            'primary_background', 'primary_pet', 'rice_quantity', 'snack_quantity', 'active_pet', 'hunger_degree_status'
        ]

    
class PetMainSerializer(PetSerializer):
    class Meta:
        model = Pet
        fields = [
            'user', 'pet_rating', 'point', 'hunger_degree_status', 'active_pet', 'primary_background', 'primary_accessory',
            'random_boxes', 'rice_quantity','snack_quantity'
            ]


class LoopUpPetSerializer(PetSerializer):
    nickname = serializers.SerializerMethodField()
    guestbook_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = ['user', 'nickname', 'pet_rating', 'point', 'hunger_degree_status', 'primary_pet', 'primary_background', 'primary_accessory', 'guestbook_url']

    def get_nickname(self, obj):
        return obj.user.nickname

    def get_guestbook_url(self, obj):
        return f'/guestbook/comments/{obj.user.id}/'


class SnackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snack
        fields = ['id', 'pet', 'snack_type', 'quantity']