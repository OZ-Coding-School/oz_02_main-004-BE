from rest_framework import serializers
from guestbook.models import GuestBookComment
from users.models import User

class GuestBookCommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField()

    class Meta:
        model = GuestBookComment
        fields = '__all__'
        extra_fields = ['user_nickname']

    def get_user_nickname(self, obj):
        return obj.user.nickname if obj.user else None


class TestGuestBookCommentSerializer(serializers.ModelSerializer):
    guestbook_user = serializers.IntegerField(required=True, help_text='This is a custom field.')

    class Meta:
        model = GuestBookComment
        fields = ['content', 'guestbook_user']

class GuestBookIdUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname']


class GuestBookCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestBookComment
        fields = ['content', 'guestbook']

    def create(self, validated_data):
        return GuestBookComment.objects.create(**validated_data)
