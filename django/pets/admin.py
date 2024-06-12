from django.contrib import admin
from .models import Accessory, Background, PetCollection, PetRating, Pet, Closet, SnackType, Snack

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'image')
    search_fields = ('item_name',)

@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'image')
    search_fields = ('item_name',)

@admin.register(PetCollection)
class PetCollectionAdmin(admin.ModelAdmin):
    list_display = ('pet_name', 'image')
    search_fields = ('pet_name',)

@admin.register(PetRating)
class PetRatingAdmin(admin.ModelAdmin):
    list_display = ('level', 'point')
    search_fields = ('level', 'point')

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('user', 'point', 'hunger_degree', 'random_boxes', 'pet_rating', 'primary_accessory', 'primary_background', 'primary_pet')
    search_fields = ('user__email', 'primary_pet__pet_name')
    list_filter = ('pet_rating',)

@admin.register(Closet)
class ClosetAdmin(admin.ModelAdmin):
    list_display = ('pet',)
    search_fields = ('pet__user__email',)
    filter_horizontal = ('accessories', 'backgrounds', 'pet_collections')

@admin.register(SnackType)
class SnackTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'experience_points')
    search_fields = ('name',)

@admin.register(Snack)
class SnackAdmin(admin.ModelAdmin):
    list_display = ('pet', 'snack_type')
    search_fields = ('pet__user__email', 'snack_type__name')
    list_filter = ('snack_type',)