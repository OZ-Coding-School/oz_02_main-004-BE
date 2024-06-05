from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
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
        user_data = [{'id': user.id, '닉네임': user.nickname, '계정': user.email, '운영진': user.is_staff, '휴면회원': user.is_down,
                      '활동회원': user.is_active, '가입일': user.created_at,}for user in users]
        return Response(user_data)

class UserDetailView(APIView):
    @swagger_auto_schema(auto_schema=None)
    # 본인 확인 로직 추가
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if (request.user != user and not request.user.is_staff):  # 본인 및 운영진만 조회가능
            return Response({'message': '본인의 정보만 확인할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN,)
        user_data = {'id': user.id, '계정': user.email, '닉네임': user.nickname, '운영진': user.is_staff, '휴면회원': user.is_down,
                     '활동회원': user.is_active, '가입일': user.created_at, '변동일': user.updated_at, '로그인': user.login_method,}
        return Response(user_data)

class MyInfoView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        responses={200: '내 정보 조회 성공', 401: '로그인이 필요합니다.'},
        operation_id='내 정보 조회 API',
        operation_description='내 정보를 조회합니다.',
    )
    def get(self, request):
        user = request.user
        user_data = {'id': user.id, '계정': user.email, '닉네임': user.nickname, '운영진': user.is_staff, '휴면회원': user.is_down,
                     '가입일자': user.created_at, '수정일자': user.updated_at, '로그인': user.login_method,}
        return Response(user_data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'action': openapi.Schema(type=openapi.TYPE_STRING)},
            required=['action'],
            example={'action': 'withdraw'},
        ),
        responses={204: '회원탈퇴가 완료되었습니다.', 400: '잘못된 요청입니다.'},
        operation_id='회원탈퇴 요청 API',
        operation_description='회원탈퇴를 요청합니다. \n\n Post 요청을 해주세요 ',
    )
    def post(self, request):
        action = request.data.get('action')
        if action == 'withdraw':
            return self.withdraw(request)
        else:
            return Response({'message': '잘못된 요청입니다.'}, status=status.HTTP_400_BAD_REQUEST)

    def withdraw(self, request):
        user = request.user
        user.is_active = False
        user.is_staff = False
        user.save()

        # 회원탈퇴 후 토큰 삭제
        response = Response({'message': '회원탈퇴가 완료되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response