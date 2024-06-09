from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from pets.models import Pet, PetRating

User = get_user_model()

@receiver(post_save, sender=User)
def create_pet_for_new_user(sender, instance, created, **kwargs):
    if created:
        Pet.objects.create(user=instance, name=f'{instance.email}_pet')


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