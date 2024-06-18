from rest_framework import serializers
from posts.models import Post, Timer, Music, ToDo, UserGoal
from django.utils import timezone


class UserGoalSerializer(serializers.ModelSerializer):
    days_by_deadline = serializers.SerializerMethodField()

    class Meta:
        model = UserGoal
        fields = ['goal', 'd_day', 'days_by_deadline']

    def get_days_by_deadline(self, goal_obj):
        if goal_obj.d_day:
            return (goal_obj.d_day - timezone.now().date()).days
        return None

    # d_day field can only have future date (>tommorow) value
    def validate_d_day(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError('D-day cannot be in the past or present.')
        return value


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
    days_by_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'user', 'feeling_status', 'todo_progress', 'todo_date',
            'memo', 'goal', 'd_day', 'days_by_deadline',
        )
        # depth = 1

    def get_days_by_deadline(self, goal_obj):
        return goal_obj.days_by_deadline


class PostCreateSerializer(serializers.ModelSerializer):
    feeling_status = serializers.ChoiceField(choices=[0, 1, 2], required=False, default=0)

    class Meta:
        model = Post
        fields = ('feeling_status', 'todo_date', 'memo')

    def create(self, validated_data):
        user = self.context['user']
        return Post.objects.create(user=user, **validated_data)

    # 새로 생성되는 todo_date는 today 이전 날짜로는 생성되지 않는다
    def validate_todo_date(self, value):
        user = self.context['user']
        print(user)

        if value < timezone.now().date():
            raise serializers.ValidationError('todo date cannot be in the past.')

        if Post.objects.filter(todo_date=value, user=user).exists():
            raise serializers.ValidationError('You already have a post for this date.')
        return value


class PostDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('todo_date',)


class SpotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = '__all__'


class SpotifySearchSerializer(serializers.Serializer):
    album = serializers.CharField(max_length=255)
    release_date = serializers.DateField()
    singer = serializers.CharField(max_length=255)
    title = serializers.CharField(max_length=255)
    song_url = serializers.URLField(allow_null=True)


class SongCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = ('singer', 'album', 'title', 'release_date', 'song_url')

    def validate(self, data):
        post = data.get('post')
        if Music.objects.filter(post=post).exists():
            raise serializers.ValidationError(f'Post {post.id} already has a music instance.')
        return data


class SpotifyQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, max_length=255)


class TimerSerializer(serializers.ModelSerializer):
    formatted_duration = serializers.SerializerMethodField()

    class Meta:
        model = Timer
        fields = ['id', 'on_btn', 'start', 'end', 'duration', 'formatted_duration',]

    def get_formatted_duration(self, obj):
        return obj.format_duration()


class TimerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = ('on_btn', 'start', 'end', 'duration')


class TimerActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['pause', 'restart', 'reset'], required=True)