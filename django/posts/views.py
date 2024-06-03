from posts.models import Post, Timer, Music
from users.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from posts.serializer import PostSerializer, SpotifySerializer, SongCreateSerializer

# spotify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# /post/list
class PostList(APIView):

    # permission_classes = [IsAuthenticated]

    # 전체 post list
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# /post/<int:member_id>
class PostsByUser(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    # 특정 유저가 대답한 모든 질문 불러오기
    def get_posts_by_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            raise NotFound

        return Post.objects.filter(user=User.objects.get(id=user_id))

    def get(self, request, user_id):
        posts = self.get_posts_by_user(user_id)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# /music/<int:post_id>
class Spotify(APIView):
    # spotify api key
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id="ef4e75402c00445ea5f79a3f8fb2648f",
                client_secret="89b9199e82fa42cd96a38ce0592d2cd5",
            )
        )

    def get_post(self, post_id):
        # get post object
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return None

    # 현재 등록된 음악 불러오기
    def get_current_song(self, post_id):
        post = self.get_post(post_id=post_id)
        if not post:
            return Response(
                {"error": "Post not found!"}, status=status.HTTP_404_NOT_FOUND
            )
        current_song = post.musics.first()
        return current_song

    def get(self, request, post_id):
        # get songs from searched results (max: 50 songs)
        query = request.data.get("query", None)
        if not query:
            return Response({"error": "Query parameter is required!"})

        try:
            post = self.get_post(post_id)
            results = self.sp.search(q=query, type="track", limit=50)
            tracks = []
            for track in results["tracks"]["items"]:
                track_data = {
                    "album": track["album"]["name"],
                    "release_date": track["album"]["release_date"],
                    "singer": track["artists"][0]["name"],
                    "title": track["name"],
                    "song_url": track["preview_url"],
                    "post": post.id,
                }
                serializer = SpotifySerializer(data=track_data)
                if serializer.is_valid():
                    # song = serializer.save()
                    tracks.append(serializer.data)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(tracks, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, post_id):
        # assumption: a certain song is selected
        """
        data = {
            "album": "abc",
            "release_date": "2018-08-24",
            "singer": "BTS",
            "title": "akdjkj",
            "song_url":"url",
        }
        """
        post = self.get_post(post_id=post_id)
        serializer = SongCreateSerializer(data=request.data)

        if serializer.is_valid():
            song = serializer.save(post=post)
            serializer = SpotifySerializer(song)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 등록된 음악을 변경할 경우
    def put(self, request, post_id):
        current_song = self.get_current_song(post_id)
        if not current_song:
            return Response(
                {"error": "Any song was not registered yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SpotifySerializer(current_song, data=request.data, partial=True)
        if serializer.is_valid():
            song = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 현재 등록된 음악 삭제
    def delete(self, request, post_id):
        current_song = self.get_current_song(post_id=post_id)
        if not current_song:
            return Response(
                {"error": "No song exists"},
                status=status.HTTP_404_NOT_FOUND,
            )

        current_song.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
