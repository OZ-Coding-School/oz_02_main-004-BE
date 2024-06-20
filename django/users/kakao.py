from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CreateUserSerializer
from drf_yasg.utils import swagger_auto_schema
from users.utils import generate_random_nickname
import requests

# Create your views here.
User = get_user_model()

class KakaoView(APIView):
    @swagger_auto_schema(
        responses={302: '카카오 로그인 페이지로 이동합니다.'},
        operation_id='카카오 로그인 API',
        operation_description='카카오 로그인 페이지로 이동합니다. \n\n Get 요청을 해주세요 \n\n따로 입력받을 파라미터는 없습니다.',
    )
    def get(self, request):
        kakao_api = 'https://kauth.kakao.com/oauth/authorize?response_type=code'
        redirect_uri = 'https://api.oz-02-main-04.xyz/api/v1/users/kakao/callback'
        # redirect_uri = 'http://localhost:8000/api/v1/users/kakao/callback'
        client_id = '92ec542f65f17550dbc2fbf553c44822'
        return redirect(f'{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}')

class KakaoCallBackView(APIView):
    @swagger_auto_schema(auto_schema=None)
    def get(self, request):
        data = {
            'grant_type': 'authorization_code',
            'client_id': '92ec542f65f17550dbc2fbf553c44822',
            'redirection_uri': 'https://api.oz-02-main-04.xyz/api/v1/users/kakao/',
            # 'redirection_uri' : 'http://localhost:8000/api/v1/users/kakao/',
            'code': request.GET['code'],
            'client_secret': 'qdl4Hfn7QhS2H9l2aKiYFJdGwpkeGcc1',
        }

        kakao_token_api = 'https://kauth.kakao.com/oauth/token'
        access_token = requests.post(kakao_token_api, data=data).json()['access_token']
        # print(access_token)

        # 카카오 토큰 정보 가져오기
        kakao_user_api = 'https://kapi.kakao.com/v2/user/me'
        header = {'Authorization': f'Bearer {access_token}'}
        kakao_user = requests.get(kakao_user_api, headers=header).json()
        # print(kakao_user)  # 제대로 받아오는지 테스트를 위한 프린트 요청

        # 카카오 계정으로 사용자 조회 또는 생성
        email = kakao_user.get('kakao_account', {}).get('email', None)
        if email:
            # 데이터베이스에서 해당 이메일을 가진 사용자 조회
            try:
                user = User.objects.get(email=email)
                # 탈퇴했던 회원이 재가입을 하는 경우인지 확인
                if not user.is_active:
                    user.is_active = True
                    user.save()

            # 사용자가 존재하지 않으면 새 사용자 생성
            except User.DoesNotExist:
                serializer = CreateUserSerializer(data={'email': email, 'nickname': generate_random_nickname()})
                if serializer.is_valid():
                    user = serializer.save()
                    user.set_unusable_password()
                    user.save()
                else:
                    return Response({'message': '잘못된 요청입니다.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST,)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # 토큰 생성
            refresh = RefreshToken.for_user(user)

            # 쿠키에 토큰 저장 (세션 쿠키로 설정)
            response = HttpResponseRedirect('https://oz-02-main-04.xyz') # 로그인 완료 시 리디렉션할 URL
            # response = HttpResponseRedirect('http://localhost:8000/api/v1/users/myinfo')
            
            # CSRF 토큰 설정
            csrf_token_value = get_token(request)
            response.set_cookie('csrftoken', csrf_token_value, domain='.oz-02-main.xyz', path='/')            

            # 배포 환경에서만 secure=True와 samesite='None' 설정
            secure_cookie = request.is_secure()
            response.set_cookie('access_token', str(refresh.access_token), domain='.oz-02-main-04.xyz', path='/')
            response.set_cookie('refresh_token', str(refresh), domain='.oz-02-main-04.xyz', path='/')
            
            return response
        else:
            return Response({'message': '카카오 계정 이메일이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST,)

class KakaoLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(responses={204: '로그아웃 되었습니다.'}, operation_id='카카오 로그아웃 API', operation_description='카카오 로그아웃을 진행합니다.',)
    def post(self, request):
        logout(request)
        kakao_token = request.user.social_auth.get(provider='kakao').extra_data['access_token']
        kakao_logout_url = 'https://kapi.kakao.com/v1/user/logout'
        headers = {'Authorization': f'Bearer {kakao_token}'}
        response = requests.post(kakao_logout_url, headers=headers)

        response = Response({'message': '로그아웃 되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        domain = '.oz-02-main-04.xyz'
        cookies_to_delete = ['access_token', 'refresh_token', 'csrftoken', 'sessionid']
        for cookie in cookies_to_delete:
            response.delete_cookie(cookie, domain=domain, path='/')

        response.data['redirect_url'] = 'https://oz-02-main-04.xyz'

        return response