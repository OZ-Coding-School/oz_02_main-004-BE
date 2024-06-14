from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), message='이미 존재하는 주소입니다.')])
    nickname = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(), message='이미 존재하는 닉네임입니다.')])

    class Meta:
        model = User
        fields = ('id', 'email', 'nickname', 'is_active', 'is_down', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), message='이미 존재하는 주소입니다.')])
    nickname = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(), message='이미 존재하는 닉네임입니다.')])

    class Meta:
        model = User
        fields = ['email', 'nickname']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_unusable_password()
        user.save()
        return user