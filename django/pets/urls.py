from django.urls import path
from .views import *

urlpatterns = [
    path('closet/accessories/<int:pet_id>/', ClosetAccessoriesView.as_view(), name='closet-accessories'),
    path('closet/backgrounds/<int:pet_id>/', ClosetBackgroundsView.as_view(), name='closet-backgrounds'),
    path('closet/pets/<int:pet_id>/', ClosetPetsView.as_view(), name='closet-pets'),
    path('closet/select-accessory/<int:pet_id>/', SelectPrimaryAccessoryView.as_view(), name='select-primary-accessory'),
    path('closet/select-background/<int:pet_id>/', SelectPrimaryBackgroundView.as_view(), name='select-primary-background'),
    path('closet/select-pet/<int:pet_id>/', SelectPrimaryPetView.as_view(), name='select-primary-pet'),
    path("mypet/<int:user_id>/", MyPetTestView.as_view(), name="mypet-test"),  # 테스트용
    path("mypet/", MyPetView.as_view(), name="mypet"),  # 테스트용
    path("feed-rice/<int:pet_id>/", FeedRiceView.as_view(), name="feed-rice"),
    path("feed-snack/<int:pet_id>/", FeedSnackView.as_view(), name="feed-snack"),
    path("open-random-box/<int:user_id>/", OpenRandomBoxView.as_view(), name="open_random_box"),
]
