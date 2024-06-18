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

    def get_rice_quantity(self, obj):
        rice_type = SnackType.objects.get(name='rice')
        rice_snack = Snack.objects.filter(pet=obj, snack_type=rice_type).first()
        return rice_snack.quantity if rice_snack else 0

    def get_snack_quantity(self, obj):
        snack_type = SnackType.objects.get(name='snack')
        snack_snack = Snack.objects.filter(pet=obj, snack_type=snack_type).first()
        return snack_snack.quantity if snack_snack else 0
    
    class Meta:
        model = Pet
        fields = [
            'user', 'point', 'hunger_degree', 'random_boxes', 'pet_rating', 'primary_accessory',
            'primary_background', 'primary_pet', 'rice_quantity', 'snack_quantity', 'active_pet'
        ]

    
class PetMainSerializer(PetSerializer):
    class Meta:
        model = Pet
        fields = [
            'user', 'point', 'hunger_degree', 'random_boxes', 'pet_rating', 'primary_accessory',
            'primary_background', 'rice_quantity','snack_quantity', 'active_pet'
            ]


class PetShareSerializer(PetSerializer):
    class Meta:
        model = Pet
        fields = [
            'user', 'point', 'hunger_degree', 'random_boxes', 'pet_rating', 'primary_accessory',
            'primary_background', 'primary_pet', 'rice_quantity','snack_quantity'
            ]

class SnackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snack
        fields = ['id', 'pet', 'snack_type', 'quantity']