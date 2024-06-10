from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import GuestBook, GuestBookComment
from .serializers import GuestBookSerializer, GuestBookCommentSerializer
from django.http import Http404

class GuestBookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        guestbooks = GuestBook.objects.filter(user=request.user)
        serializer = GuestBookSerializer(guestbooks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GuestBookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestBookCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return GuestBookComment.objects.get(pk=pk)
        except GuestBookComment.DoesNotExist:
            raise Http404

    def get(self, request, guestbook_id):
        comments = GuestBookComment.objects.filter(guestbook_id=guestbook_id)
        serializer = GuestBookCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, guestbook_id):
        guestbook = GuestBook.objects.get(pk=guestbook_id)
        serializer = GuestBookCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, guestbook=guestbook)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
