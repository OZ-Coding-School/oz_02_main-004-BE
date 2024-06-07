from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from pets.models import Pet

User = get_user_model()

@receiver(post_save, sender=User)
def create_pet_for_new_user(sender, instance, created, **kwargs):
    if created:
        Pet.objects.create(user=instance, name=f'{instance.email}_pet')