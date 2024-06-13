import random
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pets.models import Pet, SnackType, Snack, PetRating, Closet, PetCollection
from .serializers import *
from rest_framework import status
from django.db.models import Max


# Create your views here.
User = get_user_model()

class MyPetView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            # pet = Pet.objects.get(user=request.user)
            pet = Pet.objects.get(user_id=user_id)
            serializer = PetSerializer(pet)
            return Response(serializer.data)
        except Pet.DoesNotExist:
            return Response({'error': 'Pet not found'}, status=status.HTTP_404_NOT_FOUND)




class FeedRiceView(APIView):
    def post(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        snack_type = get_object_or_404(SnackType, name="rice")
        
        # Find the snack instance for the pet and the given snack type
        snack = Snack.objects.filter(pet=pet, snack_type=snack_type).first()
        
        if not snack:
            return Response({"error": "No rice available for this pet."}, status=status.HTTP_400_BAD_REQUEST)
        
        quantity = request.data.get('quantity', 1)  # Default to 1 if quantity is not provided
        
        # Check if there's enough rice
        if quantity > snack.quantity:
            return Response({"error": "Not enough rice."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Decrease rice quantity
        snack.quantity -= quantity
        snack.save()
        
        # Update pet's hunger degree to current time
        pet.hunger_degree = timezone.now()
        
        # Increase pet's point by the experience points of the rice
        total_experience = snack_type.experience_points * quantity
        pet.point += total_experience
        
        # Handle leveling up
        while pet.point >= pet.pet_rating.point:
            pet.point -= pet.pet_rating.point
            next_level = pet.pet_rating.level + 1
            max_level = PetRating.objects.aggregate(max_level=Max('level'))['max_level']
            
            if next_level > max_level:
                # Check if pet already has all pets in the closet
                closet = Closet.objects.get(pet=pet)
                all_pets = PetCollection.objects.all()
                if not all_pets.difference(closet.pet_collections.all()).exists():
                    return Response({"message": "모든종류의 펫이있습니다."}, status=status.HTTP_200_OK)
                
                # Add a random pet to the closet
                remaining_pets = all_pets.difference(closet.pet_collections.all())
                random_pet = random.choice(list(remaining_pets))
                closet.pet_collections.add(random_pet)
                return Response({"message": f"{random_pet.pet_name} added to the closet."}, status=status.HTTP_200_OK)
            
            # Increase the pet's level
            pet.pet_rating = PetRating.objects.get(level=next_level)
        
        pet.save()
        
        # Serialize the updated snack and pet information
        snack_serializer = SnackSerializer(snack)
        pet_serializer = PetSerializer(pet)
        
        return Response({
            "snack": snack_serializer.data,
            "pet": pet_serializer.data
        }, status=status.HTTP_201_CREATED)



class FeedSnackView(APIView):
    def post(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        snack_type = get_object_or_404(SnackType, name="snack")
        
        # Find the snack instance for the pet and the given snack type
        snack = Snack.objects.filter(pet=pet, snack_type=snack_type).first()
        
        if not snack:
            return Response({"error": "No snacks available for this pet."}, status=status.HTTP_400_BAD_REQUEST)
        
        quantity = request.data.get('quantity', 1)  # Default to 1 if quantity is not provided
        
        # Check if there's enough snack
        if quantity > snack.quantity:
            return Response({"error": "Not enough snacks."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Decrease snack quantity
        snack.quantity -= quantity
        snack.save()
        
        # Update pet's hunger degree to current time
        pet.hunger_degree = timezone.now()
        
        # Increase pet's point by the experience points of the snack
        total_experience = snack_type.experience_points * quantity
        pet.point += total_experience
        
        # Handle leveling up
        while pet.point >= pet.pet_rating.point:
            pet.point -= pet.pet_rating.point
            next_level = pet.pet_rating.level + 1
            max_level = PetRating.objects.aggregate(max_level=Max('level'))['max_level']
            
            if next_level > max_level:
                # Check if pet already has all pets in the closet
                closet = Closet.objects.get(pet=pet)
                all_pets = PetCollection.objects.all()
                if not all_pets.difference(closet.pet_collections.all()).exists():
                    return Response({"message": "모든종류의 펫이있습니다."}, status=status.HTTP_200_OK)
                
                # Add a random pet to the closet
                remaining_pets = all_pets.difference(closet.pet_collections.all())
                random_pet = random.choice(list(remaining_pets))
                closet.pet_collections.add(random_pet)
                return Response({"message": f"{random_pet.pet_name} added to the closet."}, status=status.HTTP_200_OK)
            
            # Increase the pet's level
            pet.pet_rating = PetRating.objects.get(level=next_level)
        
        pet.save()
        
        # Serialize the updated snack and pet information
        snack_serializer = SnackSerializer(snack)
        pet_serializer = PetSerializer(pet)
        
        return Response({
            "snack": snack_serializer.data,
            "pet": pet_serializer.data
        }, status=status.HTTP_201_CREATED)
