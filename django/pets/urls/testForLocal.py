from django.urls import path
from ..views.deploy import *
from ..views.testForLocal import *

urlpatterns = [
    path('closet/accessories/<int:pet_id>/', ClosetAccessoriesTestView.as_view(), name='closet-accessories',),
    path('closet/backgrounds/<int:pet_id>/', ClosetBackgroundsTestView.as_view(), name='closet-backgrounds',),
    path('closet/pets/<int:pet_id>/', ClosetPetsTestView.as_view(), name='closet-pets'),
    path('closet/select-accessory/<int:pet_id>/', SelectPrimaryAccessoryTestView.as_view(), name='select-primary-accessory',),
    path('closet/select-background/<int:pet_id>/', SelectPrimaryBackgroundTestView.as_view(), name='select-primary-background',),
    path('closet/select-pet/<int:pet_id>/', SelectPrimaryPetTestView.as_view(), name='select-primary-pet',),
    path('mypet/<int:user_id>/', MyPetTestView.as_view(), name='mypet-test'),
    path('feed-rice/<int:pet_id>/', FeedRiceTestView.as_view(), name='feed-rice'),
    path('feed-snack/<int:pet_id>/', FeedSnackTestView.as_view(), name='feed-snack'),
    path('open-random-box/<int:user_id>/', OpenRandomBoxTestView.as_view(), name='open_random_box',),
    path('<int:user_id>/test/', LookUpPetTestView.as_view(), name='lookup_pet_test'),
]
