from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .serializers import CreateUserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
User = get_user_model()


# 퍼미션 관련 커스텀으로 운영진 퍼미션 생성 및 추가
class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class UserListView(APIView):
    permission_classes = [IsStaffUser]

    @swagger_auto_schema(auto_schema=None)
    def get(self, request):
        users = User.objects.all()
        user_data = [
            {
                "id": user.id,
                "계정": user.email,
                "운영진": user.is_staff,
                "휴면회원": user.is_down,
                "활동회원": user.is_active,
                "가입일": user.created_at,
            }
            for user in users
        ]
        return Response(user_data)


class UserDetailView(APIView):
    @swagger_auto_schema(auto_schema=None)
    # 본인 확인 로직 추가
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if (
            request.user != user and not request.user.is_staff
        ):  # 본인 및 운영진만 조회가능
            return Response(
                {"message": "본인의 정보만 확인할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user_data = {
            "id": user.id,
            "계정": user.email,
            "닉네임": user.nickname,
            "운영진": user.is_staff,
            "휴면회원": user.is_down,
            "활동회원": user.is_active,
            "가입일": user.created_at,
            "변동일": user.updated_at,
            "로그인": user.login_method,
        }
        return Response(user_data)


class MyInfoView(APIView):

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: "내 정보 조회 성공", 401: "로그인이 필요합니다."},
        operation_id="내 정보 조회 API",
        operation_description="내 정보를 조회합니다.",
    )
    def get(self, request):
        user = request.user
        user_data = {
            "id": user.id,
            "계정": user.email,
            "운영진": user.is_staff,
            "휴면회원": user.is_down,
            "가입일자": user.created_at,
            "수정일자": user.updated_at,
            "로그인": user.login_method,
        }

        return Response(user_data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"action": openapi.Schema(type=openapi.TYPE_STRING)},
            required=["action"],
            example={"action": "withdraw"},
        ),
        responses={204: "회원탈퇴가 완료되었습니다.", 400: "잘못된 요청입니다."},
        operation_id="회원탈퇴 요청 API",
        operation_description="회원탈퇴를 요청합니다. \n\n Post 요청을 해주세요 ",
    )
    def post(self, request):
        action = request.data.get("action")

        if action == "withdraw":
            return self.withdraw(request)
        else:
            return Response(
                {"message": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

    def withdraw(self, request):
        user = request.user
        user.is_active = False
        user.is_paid = False
        user.is_staff = False
        user.save()

        # 회원탈퇴 후 토큰 삭제
        response = Response(
            {"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class KakaoView(APIView):
    @swagger_auto_schema(
        responses={302: "카카오 로그인 페이지로 이동합니다."},
        operation_id="카카오 로그인 API",
        operation_description="카카오 로그인 페이지로 이동합니다. \n\n Get 요청을 해주세요 \n\n따로 입력받을 파라미터는 없습니다.",
    )
    def get(self, request):
        kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        redirect_uri = request.GET.get(
            "redirect_uri", "https://oz-02-main-04.xyz/users/kakao/callback"
        )
        client_id = request.GET.get("client_id", "92ec542f65f17550dbc2fbf553c44822")

        return redirect(
            f"{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}"
        )


class KakaoCallBackView(APIView):
    @swagger_auto_schema(auto_schema=None)
    def get(self, request):
        data = {
            "grant_type": "authorization_code",
            "client_id": "92ec542f65f17550dbc2fbf553c44822",
            "redirection_uri": "https://oz-02-main-04.xyz/users/kakao/",
            # 'redirection_uri' : 'http://localhost:8000/users/kakao/',
            "code": request.GET["code"],
            "client_secret": "qdl4Hfn7QhS2H9l2aKiYFJdGwpkeGcc1",
        }

        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        access_token = requests.post(kakao_token_api, data=data).json()["access_token"]

        # 카카오 토큰 정보 가져오기
        kakao_user_api = "https://kapi.kakao.com/v2/user/me"
        header = {"Authorization": f"Bearer {access_token}"}
        kakao_user = requests.get(kakao_user_api, headers=header).json()
        print(kakao_user)  # 제대로 받아오는지 테스트를 위한 프린트 요청

        # 카카오 계정으로 사용자 조회 또는 생성
        email = kakao_user.get("kakao_account", {}).get("email", None)
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
                serializer = CreateUserSerializer(data={"email": email})

                if serializer.is_valid():
                    user = serializer.save()
                    user.set_unusable_password()
                    user.save()
                else:
                    return Response(
                        {"message": "잘못된 요청입니다.", "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # 토큰 생성
            refresh = RefreshToken.for_user(user)

            # 쿠키에 토큰 저장 (세션 쿠키로 설정)
            response = HttpResponseRedirect(
                "https://imexer-github-mnzs40p5w-seyoits-projects.vercel.app/profile"
            )  # 로그인 완료 시 리디렉션할 URL
            # response = HttpResponseRedirect('http://localhost:8000/users/myinfo') # 로그인 완료 시 리디렉션할 URL

            response.set_cookie(
                "access_token",
                str(refresh.access_token),
                httponly=True,
                samesite="None",
                secure=True,
            )
            response.set_cookie(
                "refresh_token",
                str(refresh),
                httponly=True,
                samesite="None",
                secure=True,
            )

            return response

        else:
            return Response(
                {"message": "카카오 계정 이메일이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class KakaoLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={204: "로그아웃 되었습니다."},
        operation_id="카카오 로그아웃 API",
        operation_description="카카오 로그아웃을 진행합니다.",
    )
    def post(self, request):
        logout(request)
        response = Response(
            {"message": "로그아웃 되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
