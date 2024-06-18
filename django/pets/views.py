from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import *

# Create your views here.
User = get_user_model()


class MyPetView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        print(request.user)
        try:
            # pet = Pet.objects.get(user=request.user)
            pet = Pet.objects.get(pk=user_id)
            serializer = PetSerializer(pet)
            return Response(serializer.data)
        except Pet.DoesNotExist:
            return Response({"error": "Pet not found"}, status=404)


class OpenRandomBoxView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_pet(self, user_id):
        return get_object_or_404(Pet, id=user_id)

    def post(self, request, user_id):
        # login 연계시 변경할 코드
        # user = request.user
        # pet = user.pet

        pet = self.get_pet(user_id)
        try:
            pet.open_random_boxes()
            return Response(
                {
                    "message": "Random box opened successfully",
                    "random_boxes": pet.random_boxes,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
