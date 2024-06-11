from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Pet

User = get_user_model()

class UserPetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')

    def test_pet_creation_for_new_user(self):
        '''Test that a pet is created for a new user.'''
        pet = Pet.objects.get(user=self.user)
        self.assertIsNotNone(pet)
        self.assertEqual(pet.name, f'{self.user.email}_pet')

    def test_only_one_pet_per_user(self):
        '''Test that only one pet is created per user.'''
        pets = Pet.objects.filter(user=self.user)
        self.assertEqual(pets.count(), 1)

    def test_unique_pet_name_per_user(self):
        '''Test that the pet name is unique per user.'''
        another_user = User.objects.create_user(email='anotheruser@example.com', password='testpass')
        pet1 = Pet.objects.get(user=self.user)
        pet2 = Pet.objects.get(user=another_user)
        self.assertNotEqual(pet1.name, pet2.name)