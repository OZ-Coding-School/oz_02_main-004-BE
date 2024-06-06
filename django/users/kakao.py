from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CreateUserSerializer
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from users.utils  import generate_random_nickname
import requests, random, string

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
            if not user.nickname:
                response = HttpResponseRedirect('https://api.oz-02-main-04.xyz/api/v1/users/nickname') # 로그인 완료 시 리디렉션할 URL
                # response = HttpResponseRedirect('http://localhost:8000/api/v1/users/nickname') # 로그인 완료 시 리디렉션할 URL
            else:
                response = HttpResponseRedirect('https://www.oz-02-main-04.xyz/profile') # 로그인 완료 시 리디렉션할 URL
                # response = HttpResponseRedirect('http://localhost:8000/api/v1/users/myinfo')

            # 배포 환경에서만 secure=True와 samesite='None' 설정
            secure_cookie = request.is_secure()
            response.set_cookie('access_token', str(refresh.access_token), httponly=True, samesite='None' if secure_cookie else 'Lax', secure=secure_cookie, domain='.oz-02-main-04.xyz', path='/')
            response.set_cookie('refresh_token', str(refresh), httponly=True, samesite='None' if secure_cookie else 'Lax', secure=secure_cookie, domain='.oz-02-main-04.xyz', path='/')
            return response
        else:
            return Response({'message': '카카오 계정 이메일이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST,)

class NicknameCreateView(APIView):
    def generate_random_nickname():
        words = [
            '사과', '바나나', '오렌지', '포도', '딸기', '키위', '복숭아', '망고', '레몬', '라임',
            '수박', '멜론', '자두', '블루베리', '라즈베리', '크랜베리', '체리', '귤', '감', '배',
            '파인애플', '코코넛', '아보카도', '석류', '무화과', '구아바', '파파야', '두리안', '망고스틴', '잭프루트',
            '스타프루트', '패션프루트', '드래곤프루트', '산딸기', '복분자', '홍시', '모과', '홍옥', '레드애플', '그린애플',
            '홍자두', '황금자두', '화이트체리', '다크체리', '샤인머스캣', '캠벨포도', '청포도', '레드포도', '블랙포도', '루비포도',
            '머스크멜론', '캔탈루프', '허니듀', '갈리아멜론', '카사바', '마라쿠자', '피타야', '페피노', '사보체', '람부탄',
            '랑사트', '살라크', '몽키애플', '자몽', '스위티', '오렌지레몬', '선플라워', '러브체리', '골든베리', '산수유',
            '석류', '홍매실', '청매실', '백도', '황도', '후루야마', '사타모', '야마모모', '크림슨피', '루비레드',
            '핫핑크', '아이보리', '라일락', '올리브', '포레스트', '세이지', '스칼렛', '터쿼이즈', '사파이어', '에메랄드',
            '옥', '진주', '다이아몬드', '루비', '토파즈', '오팔', '라피스라줄리', '가넷', '시트린', '피어리스'
        ]
        random_word = random.choice(words)
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return random_word + random_suffix
    
    def post(self, request):
        user = request.user
        nickname = request.data.get('nickname')

        # 닉네임이 없으면 무작위 닉네임 생성
        if not nickname:
            nickname = self.generate_random_nickname()

        # 닉네임 유효성 검사
        if len(nickname) > 8:
            return Response({'message': '닉네임은 최대 8자까지만 가능합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        if not nickname.isalnum():
            return Response({'message': '닉네임은 한글, 영문, 숫자로 8자만 가능합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 닉네임 중복체크
        try:
            user.nickname = nickname
            user.save()
        except IntegrityError:
            return Response({'message': '이미 존재하는 닉네임입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return redirect('https://www.oz-02-main-04.xyz/profile')
        # return redirect('http://localhost:8000/api/v1/users/myinfo')

class KakaoLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(responses={204: '로그아웃 되었습니다.'}, operation_id='카카오 로그아웃 API', operation_description='카카오 로그아웃을 진행합니다.',)
    def post(self, request):
        logout(request)
        response = Response({'message': '로그아웃 되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response