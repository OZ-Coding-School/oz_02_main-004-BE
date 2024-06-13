from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import GuestBook, GuestBookComment
from .serializers import GuestBookCommentSerializer, GuestBookIdUserSerializer
from django.http import Http404
from users.models import User
from drf_yasg.utils import swagger_auto_schema

class GuestBookViewdetail(APIView):
    # permission_classes = [IsAuthenticated]

    # api/v1/guestbook/<str:nickname>/
    def get(self, request, nickname):
        users = User.objects.filter(nickname__icontains=nickname)
        if not users.exists():
            return Response({'error': 'No users found'}, status=404)

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

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        gb = GuestBook.objects.get(user=user)

        comments = GuestBookComment.objects.filter(guestbook_id=gb.id)
        serializer = GuestBookCommentSerializer(comments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=GuestBookCommentSerializer)
    def post(self, request, user_id):
        guestbook = GuestBook.objects.get(user=user_id)
        serializer = GuestBookCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, guestbook=guestbook)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestBookCommentUpdateView(APIView):
    # permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404

    @swagger_auto_schema(request_body=GuestBookCommentSerializer)
    def post(self, request, comment_id):
        comment = self.get_object(comment_id)
        serializer = GuestBookCommentSerializer(comment, data=request.data, partial=True)
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

    def post(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)