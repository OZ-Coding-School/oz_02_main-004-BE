from rest_framework import serializers
from guestbook.models import GuestBook, GuestBookComment
from users.models import User


class GuestBookCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestBookComment
        fields = ['user', 'content', 'created_at']

class GuestBookSerializer(serializers.ModelSerializer):
    comments = GuestBookCommentSerializer(many=True, read_only=True)

    class Meta:
        model = GuestBook
        fields = ['user', 'comments']


class GuestBookIdUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname']

