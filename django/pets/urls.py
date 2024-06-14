from django.urls import path
from .views import *

urlpatterns = [
    path("mypet/<int:user_id>/", MyPetView.as_view(), name="mypet"),
    path(
        "open-random-box/<int:user_id>/",
        OpenRandomBoxView.as_view(),
        name="open_random_box",
    ),
]
