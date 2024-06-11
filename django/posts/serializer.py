from rest_framework import serializers
from posts.models import Post, Timer, Music, ToDo
from users.serializers import UserSerializer
from django.utils import timezone

class ConsecutiveDaysSerializer(serializers.Serializer):
    streak = serializers.IntegerField()

class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = '__all__'

class ToDoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = ('todo_item',)

class ToDoEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = ('todo_item', 'done')

class PostSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = '__all__'
        # depth = 1

class PostCreateSerializer(serializers.ModelSerializer):
    feeling_status = serializers.ChoiceField(choices=[0, 1, 2], required=False, default=0)

    class Meta:
        model = Post
        fields = ('feeling_status', 'todo_date', 'memo')

    # 새로 생성되는 todo_date는 today 이전 날짜로는 생성되지 않는다
    def validate_todo_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError('todo date cannot be in the past.')

        user = self.context.get('user_id')
        print(user)
        # user = self.context['request'].user
        if Post.objects.filter(todo_date=value, user=user).exists():
            raise serializers.ValidationError('You already have a post for this date.')
        return value

class PostDeleteSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ('todo_date',)

class SpotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = '__all__'

class SongCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = ('singer', 'album', 'title', 'release_date', 'song_url')

class SpotifyQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, max_length=255)

class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = '__all__'

class TimerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = ('on_btn', 'start', 'end', 'duration')

class TimerActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['pause', 'restart', 'reset'], required=True)