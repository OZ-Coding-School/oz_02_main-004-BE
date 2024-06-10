from rest_framework import serializers
from .models import GuestBook, GuestBookComment

class GuestBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestBook
        fields = '__all__'

class GuestBookCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestBookComment
        fields = '__all__'
