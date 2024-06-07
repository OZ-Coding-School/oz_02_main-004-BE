from rest_framework.serializers import ModelSerializer, ValidationError
from posts.models import Post, Timer, Music, ToDo
from users.serializers import UserSerializer
from django.utils import timezone
from rest_framework import serializers

class ToDoSerializer(ModelSerializer):
    class Meta:
        model = ToDo
        fields = '__all__'

class ToDoCreateSerializer(ModelSerializer):
    class Meta:
        model = ToDo
        fields = ('todo_item',)

class PostSerializer(ModelSerializer):
    # user = UserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = '__all__'
        # depth = 1

class PostCreateSerializer(ModelSerializer):
    feeling_status = serializers.ChoiceField(choices=[0, 1, 2], required=False, default=0)

    class Meta:
        model = Post
        fields = ('feeling_status', 'todo_date', 'memo')

    # 새로 생성되는 todo_date는 today 이전 날짜로는 생성되지 않는다
    def validate_todo_date(self, value):
        if value < timezone.now().date():
            raise ValidationError('todo date cannot be in the past.')
        
        user = self.context.get('user_id')
        print(user)
        # user = self.context['request'].user
        if Post.objects.filter(todo_date=value, user=user).exists():
            raise ValidationError('You already have a post for this date.')
        return value




class SpotifySerializer(ModelSerializer):
    class Meta:
        model = Music
        fields = '__all__'

class SongCreateSerializer(ModelSerializer):
    class Meta:
        model = Music
        fields = ('singer', 'album', 'title', 'release_date', 'song_url')

class TimerSerializer(ModelSerializer):
    class Meta:
        model = Timer
        fields = '__all__'

class TimerCreateSerializer(ModelSerializer):
    class Meta:
        model = Timer
        fields = ('on_btn', 'start', 'end', 'duration')