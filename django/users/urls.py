from django.urls import path
from .userviews import UserListView, UserDetailView, MyInfoView
from .kakao import KakaoView, KakaoCallBackView, KakaoLogoutView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('myinfo/', MyInfoView.as_view(), name='my-info'),    
    path('kakao/', KakaoView.as_view()),
    path('kakao/callback', KakaoCallBackView.as_view()),    
    path('kakao/logout/', KakaoLogoutView.as_view(), name='kakao-logout'),
]