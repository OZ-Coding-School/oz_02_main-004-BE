from django.urls import path
from ..views.deploy import *

urlpatterns = [
    path('mypet/', MyPetView.as_view(), name='mypet'),
    path('open-random-box/', OpenRandomBoxView.as_view(), name='open_random_box'),
    path('feed-snack/', FeedSnackView.as_view(), name='feed-snack'),
    path('feed-rice/', FeedRiceView.as_view(), name='feed-rice'),
    path('closet/select-pet/', SelectPrimaryPetView.as_view(), name='select-primary-pet'),
    path('closet/select-accessory/', SelectPrimaryAccessoryView.as_view(), name='select-primary-accessory',),
    path('closet/select-background/', SelectPrimaryBackgroundView.as_view(), name='select-primary-background',),
    path('closet/accessories/', ClosetAccessoriesView.as_view(), name='closet-accessories',),
    path('closet/backgrounds/', ClosetBackgroundsView.as_view(), name='closet-backgrounds',),
    path('closet/pets/', ClosetPetsView.as_view(), name='closet-pets'),
    path('<int:user_id>/', LookUpPetView.as_view(), name='lookup_pet'),
]