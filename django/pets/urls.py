from django.urls import path
from .views import *

urlpatterns = [
    path('mypet/<int:user_id>/', MyPetView.as_view(), name='mypet'),
    path('feed-rice/<int:pet_id>/', FeedRiceView.as_view(), name='feed-rice'),
    path('feed-snack/<int:pet_id>/', FeedSnackView.as_view(), name='feed-snack'),
    ]