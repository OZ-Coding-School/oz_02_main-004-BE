from django.urls import path, include
from .views import UserListView, UserDetailView, MyInfoView, KakaoView, KakaoCallBackView, KakaoLogoutView, NicknameCreateView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('myinfo/', MyInfoView.as_view(), name='my-info'),    
    path('kakao/', KakaoView.as_view()),
    path('kakao/callback', KakaoCallBackView.as_view()),
    path('nickname/', NicknameCreateView.as_view(), name='create-nickname'),
    path('kakao/logout/', KakaoLogoutView.as_view(), name='kakao-logout'),
]