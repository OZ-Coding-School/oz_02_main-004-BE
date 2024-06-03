from rest_framework.serializers import ModelSerializer
from posts.models import Post, Timer, Music
from users.serializers import UserSerializer


class PostSerializer(ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"
        # depth = 1


class SpotifySerializer(ModelSerializer):
    class Meta:
        model = Music
        fields = "__all__"


class SongCreateSerializer(ModelSerializer):
    class Meta:
        model = Music
        fields = ("singer", "album", "title", "release_date", "song_url")
