from rest_framework.serializers import ModelSerializer, ValidationError
from posts.models import Post, Timer, Music, ToDo
from users.serializers import UserSerializer
from django.utils import timezone

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
    class Meta:
        model = Post
        fields = ('feeling_status', 'todo_progress', 'todo_date', 'memo')

    # 새로 생성되는 todo_date는 today 이전 날짜로는 생성되지 않는다
    def validate_todo_date(self, value):
        if value < timezone.now().date():
            raise ValidationError('todo date cannot be in the past.')
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