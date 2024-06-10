from django.urls import path
from .views import *

urlpatterns = [
    path('mypet/', MyPetView.as_view(), name='mypet'),    
]