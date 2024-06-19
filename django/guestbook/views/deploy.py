from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import GuestBook, GuestBookComment
from ..serializers import *
from django.http import Http404
from users.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class GuestBookViewdetail(APIView):
    
    # api/v1/guestbook/<str:nickname>/
    @swagger_auto_schema(
        operation_summary='유저의 닉네임으로 유저 ID 검색',
        operation_description='유저 닉네임에 해당 문자열이 포함된 모든 유저 ID를 검색합니다.',
        manual_parameters=[openapi.Parameter('nickname', openapi.IN_PATH, description='유저 닉네임', type=openapi.TYPE_STRING,),],
        tags=['방명록'],
    )
    def get(self, request, nickname):
        users = User.objects.filter(nickname__icontains=nickname)
        if not users.exists():
            return Response({'error': 'No users found'}, status=404)

        serializer = GuestBookIdUserSerializer(users, many=True)
        return Response(serializer.data)

class GuestBookView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 4 ) 로그인중인 유저의 방명록 조회',
        operation_description='로그인 중인 유저의 방명록 리스트 조회',
        tags=['방명록'],
    )
    def get(self, request):
        user = User.objects.get(email=request.user)
        gb = GuestBook.objects.get(user=user)

        comments = GuestBookComment.objects.filter(guestbook_id=gb.id)
        serializer = GuestBookCommentSerializer(comments, many=True)
        return Response(serializer.data)

class GuestBookCommentView(APIView):
    @swagger_auto_schema(
        operation_summary='방명록의 전체 게시물 조회',
        operation_description='조회 원하는 유저를 path 파라미터에 입력',
        manual_parameters=[openapi.Parameter('user_id', openapi.IN_PATH, description='검색원하는 유저 ID', type=openapi.TYPE_INTEGER,),],
        tags=['방명록'],
    )
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        gb = GuestBook.objects.get(user=user)
        comments = GuestBookComment.objects.filter(guestbook_id=gb.id)
        serializer = GuestBookCommentSerializer(comments, many=True)
        return Response(serializer.data)

class GuestBookCommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 3 ) 방명록에 게시물 추가',
        operation_description='배포시 /guestbook/comments/ 이 주소로 바뀔예정입니다.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='게시물의 내용',),
                'guestbook_user': openapi.Schema(type=openapi.TYPE_INTEGER, description='방명록을 소유하고 있는 유저 ID',),
            },
        ),
        tags=['방명록'],
    )
    def post(self, request):
        guestbook_user_id = request.data.get('guestbook_user')
        content = request.data.get('content')

        if not guestbook_user_id or not content:
            return Response({'error': 'guestbook_user and content are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        guestbook_user = get_object_or_404(User, id=guestbook_user_id)
        guestbook = get_object_or_404(GuestBook, user=guestbook_user)

        data = {'content': content, 'guestbook': guestbook.id, 'user': request.user.id}

        serializer = GuestBookCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestBookCommentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404

    def has_permission_to_update(self, user, comment):
        # Check if the comment belongs to the user's guestbook
        # if comment.guestbook.user == user:
        #     return True
        # Check if the comment was written by the user
        if comment.user == user:
            return True
        return False

    @swagger_auto_schema(
        operation_summary='( 2 ) 방명록에 게시물 수정하기',
        operation_description='/guestbook/comments/{user_id}/에서 comment_id 조회가능 \n 로그인한 유저가 작성한 방명록만 수정가능. (방명록 소유자여도 수정불가.)',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='삭제를 원하는 방명록 게시물 ID',),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='수정원하는 게시물의 내용'),
            },
        ),
        tags=['방명록'],
    )
    def post(self, request):
        comment = self.get_object(request.data['comment_id'])

        if not self.has_permission_to_update(request.user, comment):
            return Response({'error': 'You do not have permission to update this comment.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['user'] = request.user.id  # Ensure the user is the current logged-in user
        serializer = GuestBookCommentSerializer(comment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data
            response_data['message'] = '수정완료'
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestBookCommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404

    def has_permission_to_delete(self, user, comment):
        # Check if the comment belongs to the user's guestbook
        if comment.guestbook.user == user:
            return True
        # Check if the comment was written by the user
        if comment.user == user:
            return True
        return False

    @swagger_auto_schema(
        operation_summary='( 1 ) 방명록에 게시물 삭제',
        operation_description='/guestbook/comments/{user_id}/에서 comment_id 조회가능 \n 방명록의 소유자 이거나, 방명록 작성자만 삭제가능.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='삭제를 원하는 방명록 게시물 ID',),},
        ),
        tags=['방명록'],
    )
    def post(self, request):
        comment = self.get_object(request.data['comment_id'])
        
        if not self.has_permission_to_delete(request.user, comment):
            return Response({'error': 'You do not have permission to delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response({'message': '삭제완료'}, status=status.HTTP_200_OK)