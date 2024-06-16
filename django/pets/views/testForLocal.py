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


class MyPetTestView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 1 ) 유저 ID의 펫 메인페이지 정보 조회 ★ 배포시 삭제예정 ★',
        operation_description='유저 ID의 펫 메인페이지 정보 조회 합니다.',
        manual_parameters=[openapi.Parameter('user_id', openapi.IN_PATH, description='유저 ID', type=openapi.TYPE_INTEGER),],
        tags=['펫'],
    )
    def get(self, request, user_id):
        try:
            # pet = Pet.objects.get(user=request.user)
            pet = Pet.objects.get(user_id=user_id)
            serializer = PetSerializer(pet)
            return Response(serializer.data)
        except Pet.DoesNotExist:
            return Response(
                {"error": "Pet not found"}, status=status.HTTP_404_NOT_FOUND
            )

