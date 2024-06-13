from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import GuestBook, GuestBookComment
from .serializers import (
    GuestBookCommentSerializer,
    GuestBookIdUserSerializer,
    TestGuestBookCommentSerializer,
)
from django.http import Http404
from users.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GuestBookViewdetail(APIView):
    # permission_classes = [IsAuthenticated]

    # api/v1/guestbook/<str:nickname>/
    def get(self, request, nickname):
        users = User.objects.filter(nickname__icontains=nickname)
        if not users.exists():
            return Response({"error": "No users found"}, status=404)

        serializer = GuestBookIdUserSerializer(users, many=True)
        return Response(serializer.data)


class GuestBookView(APIView):
    # permission_classes = [IsAuthenticated]

    # api/v1/guestbook/
    # def get(self, request):
    #     user = User.objects.get(email=request.user)
    def get(self, request, nickname):
        user = User.objects.get(nickname=nickname)
        gb = GuestBook.objects.get(user=user)

        comments = GuestBookComment.objects.filter(guestbook_id=gb.id)
        serializer = GuestBookCommentSerializer(comments, many=True)
        return Response(serializer.data)


class GuestBookCommentView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404
        

    @swagger_auto_schema(
        operation_summary="방명록의 전체 게시물 조회",
        operation_description="조회 원하는 유저를 path 파라미터에 입력",
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_PATH,
                description="검색원하는 유저 ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        tags=["방명록"],
    )
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        gb = GuestBook.objects.get(user=user)
        comments = GuestBookComment.objects.filter(guestbook_id=gb.id)
        serializer = GuestBookCommentSerializer(comments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="방명록에 게시물 추가",
        operation_description="배포시 /guestbook/comments/ 이 주소로 바뀔예정입니다.",
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_PATH,
                description="로그인중인 유저 ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="게시물의 내용",
                ),
                "guestbook_user": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="방명록을 소유하고 있는 유저 ID",
                ),
            },
        ),
        # responses={
        #     201: openapi.Response(
        #         description="Comment created successfully",
        #         schema=openapi.Schema(
        #             type=openapi.TYPE_OBJECT,
        #             properties={
        #                 "id": openapi.Schema(
        #                     type=openapi.TYPE_INTEGER, description="ID of the comment."
        #                 ),
        #                 "user": openapi.Schema(
        #                     type=openapi.TYPE_INTEGER,
        #                     description="ID of the user posting the comment.",
        #                 ),
        #                 "content": openapi.Schema(
        #                     type=openapi.TYPE_STRING,
        #                     description="Content of the guestbook comment.",
        #                 ),
        #                 "custom_response_field": openapi.Schema(
        #                     type=openapi.TYPE_STRING,
        #                     description="This is a custom response field.",
        #                 ),
        #             },
        #         ),
        #     ),
        #     400: openapi.Response(description="Bad Request"),
        #     404: openapi.Response(description="Not Found"),
        # },
        tags=["방명록"],
    )
    def post(self, request, user_id):
        user_email = User.objects.get(id=user_id)
        guestbook = GuestBook.objects.get(user=request.data["guestbook_user"])
        request.data["guestbook"] = guestbook.id
        request.data["user"] = user_id
        serializer = GuestBookCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user_email)
            # serializer.save(user=request.user, guestbook=guestbook)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestBookCommentUpdateView(APIView):
    # permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404
        
    @swagger_auto_schema(
        operation_summary="방명록에 게시물 수정하기",
        operation_description="/guestbook/comments/{user_id}/에서 comment_id 조회가능",
        manual_parameters=[
            openapi.Parameter(
                "comment_id",
                openapi.IN_PATH,
                description="수정을 원하는 방명록 게시물 ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="수정원하는 게시물의 내용",
                ),
                "user": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="현재 로그인 중인 유저 ID",
                ),
            },
        ),
        tags=["방명록"],
    )
    @swagger_auto_schema(request_body=GuestBookCommentSerializer)
    def post(self, request, comment_id):
        comment = self.get_object(comment_id)
        serializer = GuestBookCommentSerializer(
            comment, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestBookCommentDeleteView(APIView):
    # permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404


    @swagger_auto_schema(
        operation_summary="방명록에 게시물 삭제",
        operation_description="/guestbook/comments/{user_id}/에서 comment_id 조회가능",
        manual_parameters=[
            openapi.Parameter(
                "comment_id",
                openapi.IN_PATH,
                description="삭제를 원하는 방명록 게시물 ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        tags=["방명록"],
    )
    def post(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
