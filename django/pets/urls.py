from django.urls import path
from .views import *

urlpatterns = [
    path('mypet/<int:user_id>/', MyPetView.as_view(), name='mypet'),    
]