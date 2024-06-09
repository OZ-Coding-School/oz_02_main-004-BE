from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *

# Create your views here.
User = get_user_model()

class PetListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self):
        return Response(self.request)