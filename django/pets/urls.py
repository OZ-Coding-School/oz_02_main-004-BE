from django.urls import path
from .views import *

urlpatterns = [
    path('', PetListView.as_view(), name='user-list'),    
]