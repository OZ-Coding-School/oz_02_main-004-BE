from rest_framework import serializers
from guestbook.models import GuestBookComment
from users.models import User

class GuestBookCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestBookComment
        fields = '__all__'

class TestGuestBookCommentSerializer(serializers.ModelSerializer):
    guestbook_user = serializers.IntegerField(required=True, help_text='This is a custom field.')

    class Meta:
        model = GuestBookComment
        fields = ['content', 'guestbook_user']

class GuestBookIdUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname']