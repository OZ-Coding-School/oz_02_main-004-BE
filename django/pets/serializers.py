from rest_framework import serializers
from .models import Pet, Accessory, Background, PetCollection, Snack

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

class PetSerializer(serializers.ModelSerializer):
    primary_accessory = AccessorySerializer()
    primary_background = BackgroundSerializer()
    primary_pet = PetCollectionSerializer()

    class Meta:
        model = Pet
        fields = ['user', 'point', 'hunger_degree', 'random_boxes', 'pet_rating', 'primary_accessory', 'primary_background', 'primary_pet']
