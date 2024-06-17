import random
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pets.models import Pet, SnackType, Snack, PetRating, Closet, PetCollection
from ..serializers import *
from rest_framework import status
from django.db.models import Max
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
User = get_user_model()


class MyPetView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 1 ) 펫 메인페이지 정보 조회 - MainPage',
        operation_description='현재 로그인 중인 유저의 펫 메인페이지 정보를 조회 합니다.',
        tags=['펫'],
    )
    def get(self, request):
        try:
            pet = Pet.objects.get(user=request.user)
            serializer = PetMainSerializer(pet)
            return Response(serializer.data)
        except Pet.DoesNotExist:
            return Response(
                {"error": "Pet not found"}, status=status.HTTP_404_NOT_FOUND
            )

class FeedRiceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 4 ) - MainPage',
        tags=['펫'],
    )
    def post(self, request):
        pet = get_object_or_404(Pet, user=request.user)
        snack_type = get_object_or_404(SnackType, name="rice")

        # Find the snack instance for the pet and the given snack type
        snack = Snack.objects.filter(pet=pet, snack_type=snack_type).first()

        if not snack:
            return Response(
                {"error": "No rice available for this pet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantity = request.data.get(
            "quantity", 1
        )  # Default to 1 if quantity is not provided

        # Check if there's enough rice
        if quantity > snack.quantity:
            return Response(
                {"error": "Not enough rice."}, status=status.HTTP_400_BAD_REQUEST
            )

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
            max_level = PetRating.objects.aggregate(max_level=Max("level"))["max_level"]

            if next_level > max_level:
                # Set pet back to level 1 and change active pet to "수상한 알"
                pet.pet_rating = PetRating.objects.get(level=1)
                suspicious_egg = get_object_or_404(PetCollection, pet_name="수상한 알")
                pet.active_pet = suspicious_egg
            else:
                # Get or create the closet for the pet
                closet, created = Closet.objects.get_or_create(pet=pet)
                if created:
                    suspicious_egg = get_object_or_404(
                        PetCollection, pet_name="수상한 알"
                    )
                    closet.pet_collections.add(suspicious_egg)

                # Add a random pet to the closet when leveling up
                all_pets = PetCollection.objects.all()
                remaining_pets = all_pets.difference(closet.pet_collections.all())

                if remaining_pets.exists():
                    random_pet = random.choice(list(remaining_pets))
                    closet.pet_collections.add(random_pet)
                    # Set the new pet as active if leveling from 1 to 2
                    if next_level == 2:
                        pet.active_pet = random_pet
                else:
                    if next_level == 2:
                        return Response(
                            {"message": "모든종류의 펫을모았습니다."},
                            status=status.HTTP_200_OK,
                        )

                pet.pet_rating = PetRating.objects.get(level=next_level)

        pet.save()

        # Serialize the updated snack and pet information
        snack_serializer = SnackSerializer(snack)
        pet_serializer = PetSerializer(pet)

        return Response(
            {"snack": snack_serializer.data, "pet": pet_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class FeedSnackView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 3 ) - MainPage',
        tags=['펫'],
    )
    def post(self, request):
        pet = get_object_or_404(Pet, user=request.user)
        snack_type = get_object_or_404(SnackType, name="snack")

        # Find the snack instance for the pet and the given snack type
        snack = Snack.objects.filter(pet=pet, snack_type=snack_type).first()

        if not snack:
            return Response(
                {"error": "No snacks available for this pet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantity = request.data.get(
            "quantity", 1
        )  # Default to 1 if quantity is not provided

        # Check if there's enough snack
        if quantity > snack.quantity:
            return Response(
                {"error": "Not enough snacks."}, status=status.HTTP_400_BAD_REQUEST
            )

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
            max_level = PetRating.objects.aggregate(max_level=Max("level"))["max_level"]

            if next_level > max_level:
                # Set pet back to level 1 and change active pet to "수상한 알"
                pet.pet_rating = PetRating.objects.get(level=1)
                suspicious_egg = get_object_or_404(PetCollection, pet_name="수상한 알")
                pet.active_pet = suspicious_egg
            else:
                # Get or create the closet for the pet
                closet, created = Closet.objects.get_or_create(pet=pet)
                if created:
                    suspicious_egg = get_object_or_404(
                        PetCollection, pet_name="수상한 알"
                    )
                    closet.pet_collections.add(suspicious_egg)

                # Add a random pet to the closet when leveling up
                all_pets = PetCollection.objects.all()
                remaining_pets = all_pets.difference(closet.pet_collections.all())

                if remaining_pets.exists():
                    random_pet = random.choice(list(remaining_pets))
                    closet.pet_collections.add(random_pet)
                    # Set the new pet as active if leveling from 1 to 2
                    if next_level == 2:
                        pet.active_pet = random_pet
                else:
                    if next_level == 2:
                        return Response(
                            {"message": "모든종류의 펫을모았습니다."},
                            status=status.HTTP_200_OK,
                        )

                pet.pet_rating = PetRating.objects.get(level=next_level)

        pet.save()

        # Serialize the updated snack and pet information
        snack_serializer = SnackSerializer(snack)
        pet_serializer = PetSerializer(pet)

        return Response(
            {"snack": snack_serializer.data, "pet": pet_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class OpenRandomBoxView(APIView):
    permission_classes = [IsAuthenticated]

    def get_pet(self, request_user):
        return get_object_or_404(Pet, user=request_user)
    
    @swagger_auto_schema(
        operation_summary='( 2 ) - RandomBox',
        tags=['펫'],
    )
    def post(self, request):
        pet = self.get_pet(request.user)
        try:
            output_item = pet.open_random_boxes()
            return Response(
                {
                    "message": "Random box opened successfully",
                    "random_boxes": pet.random_boxes,
                    "output_item": output_item,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClosetAccessoriesView(APIView):
    @swagger_auto_schema(
        operation_summary='( 8 ) - Closet',
        tags=['펫'],
    )
    def get(self, request):
        pet = get_object_or_404(Pet, user=request.user)
        closet = get_object_or_404(Closet, pet=pet)
        accessories = closet.accessories.all()
        serializer = AccessorySerializer(accessories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClosetBackgroundsView(APIView):
    @swagger_auto_schema(
        operation_summary='( 9 ) - Closet',
        tags=['펫'],
    )
    def get(self, request):
        pet = get_object_or_404(Pet, user=request.user)
        closet = get_object_or_404(Closet, pet=pet)
        backgrounds = closet.backgrounds.all()
        serializer = BackgroundSerializer(backgrounds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClosetPetsView(APIView):
    @swagger_auto_schema(
        operation_summary='( 10 ) - Closet',
        tags=['펫'],
    )
    def get(self, request):
        pet = get_object_or_404(Pet, user=request.user)
        closet = get_object_or_404(Closet, pet=pet)
        pets = closet.pet_collections.all()
        serializer = PetCollectionSerializer(pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SelectPrimaryAccessoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 6 ) - Closet',
        tags=['펫'],            
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "item_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="선택하는 아이템 이름",
                ),
            },
        ),
    )
    def post(self, request):
        pet = get_object_or_404(Pet, user=request.user)
        item_name = request.data.get("item_name")
        accessory = get_object_or_404(Accessory, item_name=item_name)

        closet = pet.closets.first()
        if accessory not in closet.accessories.all():
            return Response(
                {"error": "Accessory not in closet"}, status=status.HTTP_400_BAD_REQUEST
            )

        pet.primary_accessory = accessory
        pet.save()

        return Response(
            {"message": "Primary accessory selected successfully"},
            status=status.HTTP_200_OK,
        )


class SelectPrimaryBackgroundView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 7 ) - Closet',
        tags=['펫'],            
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "item_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="선택하는 아이템 이름",
                ),
            },
        ),
    )
    def post(self, request, pet_id):
        pet = get_object_or_404(Pet, user=request.user)
        item_name = request.data.get("item_name")
        background = get_object_or_404(Background, item_name=item_name)

        closet = pet.closets.first()
        if background not in closet.backgrounds.all():
            return Response(
                {"error": "Background not in closet"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pet.primary_background = background
        pet.save()

        return Response(
            {"message": "Primary background selected successfully"},
            status=status.HTTP_200_OK,
        )


class SelectPrimaryPetView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 5 ) - Closet',
        tags=['펫'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "item_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="선택하는 펫 이름",
                ),
            },
        ),
    )
    def post(self, request):
        pet = get_object_or_404(Pet, user=request.user)
        item_name = request.data.get("item_name")
        selected_pet = get_object_or_404(PetCollection, pet_name=item_name)

        closet = pet.closets.first()
        if selected_pet not in closet.pet_collections.all():
            return Response(
                {"error": "Pet not in closet"}, status=status.HTTP_400_BAD_REQUEST
            )

        pet.primary_pet = selected_pet
        pet.save()

        return Response(
            {"message": "Primary pet selected successfully"}, status=status.HTTP_200_OK
        )


class LookUpPetView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 11 ) - Guest',
        tags=['펫'],
    )
    def get(self, request, user_id):
        try:
            pet = Pet.objects.get(user_id=user_id)
            serializer = LoopUpPetSerializer(pet)
            return Response(serializer.data)
        except Pet.DoesNotExist:
            return Response(
                {"error": "Pet not found"}, status=status.HTTP_404_NOT_FOUND
            )
