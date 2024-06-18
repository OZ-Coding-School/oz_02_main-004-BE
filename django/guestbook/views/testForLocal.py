from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import GuestBook, GuestBookComment
from ..serializers import GuestBookCommentSerializer
from django.http import Http404
from users.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GuestBookTestView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='( 4 ) 유저의 닉네임으로 유저 ID 검색 ★ 배포시 삭제예정 ★',
        operation_description='정확히 일치하는 유저 닉네임의 방명록의 게시물 ID를 검색합니다.  배포시 /guestbook/ 으로 변경 예정',
        manual_parameters=[openapi.Parameter('nickname', openapi.TYPE_STRING, description='유저 닉네임', type=openapi.TYPE_INTEGER,),],
        tags=['방명록'],
    )
    # api/v1/guestbook/
    # def get(self, request):
    #     user = User.objects.get(email=request.user)
    def get(self, request, nickname):
        user = User.objects.get(nickname=nickname)
        gb = GuestBook.objects.get(user=user)

        comments = GuestBookComment.objects.filter(guestbook_id=gb.id)
        serializer = GuestBookCommentSerializer(comments, many=True)
        return Response(serializer.data)

class GuestBookCommentTestView(APIView):
    @swagger_auto_schema(
        operation_summary='( 3 ) 방명록에 게시물 추가 ★ 배포시 삭제예정 ★',
        operation_description='배포시 /guestbook/comments/ 이 주소로 바뀔예정입니다.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인중인 유저 ID',),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='게시물의 내용',),
                'guestbook_user': openapi.Schema(type=openapi.TYPE_INTEGER, description='방명록을 소유하고 있는 유저 ID',),
            },
        ),
        # responses={
        #     201: openapi.Response(
        #         description='Comment created successfully',
        #         schema=openapi.Schema(
        #             type=openapi.TYPE_OBJECT,
        #             properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the comment.'),
        #                 'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user posting the comment.',),
        #                 'content': openapi.Schema(type=openapi.TYPE_STRING, description='Content of the guestbook comment.',),
        #                 'custom_response_field': openapi.Schema(type=openapi.TYPE_STRING, description='This is a custom response field.',),
        #             },
        #         ),
        #     ),
        #     400: openapi.Response(description='Bad Request'),
        #     404: openapi.Response(description='Not Found'),
        # },
        tags=['방명록'],
    )
    def post(self, request):
        user_id = request.data['user_id']
        user_email = User.objects.get(id=user_id)
        guestbook = GuestBook.objects.get(user=request.data['guestbook_user'])
        request.data['guestbook'] = guestbook.id
        request.data['user'] = user_id
        serializer = GuestBookCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user_email)
            # serializer.save(user=request.user, guestbook=guestbook)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestBookCommentUpdateTestView(APIView):
    # permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404
        
    @swagger_auto_schema(
        operation_summary='( 2 ) 방명록에 게시물 수정하기 ★ 배포시 삭제예정 ★',
        operation_description='/guestbook/comments/{user_id}/에서 comment_id 조회가능',
        manual_parameters=[openapi.Parameter('comment_id', openapi.IN_PATH, description='수정을 원하는 방명록 게시물 ID', type=openapi.TYPE_INTEGER,),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'content': openapi.Schema(type=openapi.TYPE_STRING, description='수정원하는 게시물의 내용',),
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='현재 로그인 중인 유저 ID',),
            },
        ),
        tags=['방명록'],
    )
    def post(self, request, comment_id):
        comment = self.get_object(comment_id)
        serializer = GuestBookCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestBookCommentDeleteTestView(APIView):
    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_summary='( 1 ) 방명록에 게시물 삭제 ★ 배포시 삭제예정 ★',
        operation_description='/guestbook/comments/{user_id}/에서 comment_id 조회가능',
        manual_parameters=[openapi.Parameter('comment_id', openapi.IN_PATH, description='삭제를 원하는 방명록 게시물 ID', type=openapi.TYPE_INTEGER,),],
        tags=['방명록'],
    )
    def post(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)