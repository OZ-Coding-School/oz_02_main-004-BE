from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
            return Response({'error': 'Pet not found'}, status=404)
