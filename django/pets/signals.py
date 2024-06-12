from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from pets.models import Pet, PetRating, Background, PetCollection
from guestbook.models import GuestBook

User = get_user_model()

@receiver(post_save, sender=User)
def create_pet_for_new_user(sender, instance, created, **kwargs):
    if created:
        default_rating, _ = PetRating.objects.get_or_create(level=1, point=100)
        default_background, _ = Background.objects.get_or_create(item_name='봄')
        default_pet_collection, _ = PetCollection.objects.get_or_create(pet_name='수상한 알')

        Pet.objects.create(user=instance, pet_rating=default_rating, primary_background=default_background, primary_pet=default_pet_collection)

        GuestBook.objects.create(user=instance)

@receiver(post_migrate)
def create_initial_pet_ratings(sender, **kwargs):
    print(sender.name)
    if sender.name == 'pets':
        if not PetRating.objects.exists():
            initial_data = [
                {'level': 1, 'point': 100},
                {'level': 2, 'point': 150},
            ]
            for data in initial_data:
                PetRating.objects.create(**data)

# Signals to set default values for Pet model
@receiver(post_save, sender=Pet)
def set_default_pet_items(sender, instance, created, **kwargs):
    if created:
        instance.primary_background = Background.get_default_background()
        instance.primary_pet = PetCollection.get_default_pet()
        instance.save()