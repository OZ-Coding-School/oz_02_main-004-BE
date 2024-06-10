import json
from django.conf import settings
from posts.models import Post, Timer, ToDo
from users.models import User
from users.userviews import IsStaffUser
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from posts.serializer import (
    PostSerializer,
    PostCreateSerializer,
    PostDeleteSerializer,
    SpotifySerializer,
    SpotifyQuerySerializer,
    SongCreateSerializer,
    TimerSerializer,
    TimerCreateSerializer,
    TimerActionSerializer,
    ToDoSerializer,
    ToDoEditSerializer,
    ToDoCreateSerializer,
)
from drf_yasg.utils import swagger_auto_schema

# spotify
# reference : https://spotipy.readthedocs.io/en/2.24.0/#examples
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# /post/list
class PostList(APIView):
    # todo: 관리자만 접근 가능하도록 변경할것
    # permission_classes = [IsAuthenticated, IsStaffUser]

    # 전체 post list
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# /post/<int:user_id>
class PostsByUser(APIView):
    # todo: 로그인한 해당 유저만 접근가능
    # permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        return get_object_or_404(User, id=user_id)

    # get post list written by a certain user
    def get_posts_by_user(self, user_id):
        user = self.get_user(user_id)
        return Post.objects.filter(user=user)

    # get the post written on a certain day by user
    def get_post(self, user_id, target_date):
        user = self.get_user(user_id)
        return Post.objects.filter(user=user, todo_date=target_date).first()

    def get(self, request, user_id):
        # if request.user.id != user_id:
        #     return Response({"error": "You do not have permission to access these posts."}, status=status.HTTP_403_FORBIDDEN)

        posts = self.get_posts_by_user(user_id)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PostCreateSerializer)
    def post(self, request, user_id):
        user = self.get_user(user_id=user_id)
        serializer = PostCreateSerializer(
            data=request.data, context={"user_id": user_id}
        )
        if serializer.is_valid():
            post = serializer.save(user=user)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 포스트 내용 변경 : 'todo_date' is required
    @swagger_auto_schema(request_body=PostCreateSerializer)
    def put(self, request, user_id):
        target_date = request.data.get("todo_date")
        post = self.get_post(user_id=user_id, target_date=target_date)
        if not post:
            return Response(
                {"error": "Post Not Found"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 포스트 삭제 : 'todo_date' is required
    @swagger_auto_schema(request_body=PostDeleteSerializer)
    def delete(self, request, user_id):
        target_date = request.data.get("todo_date")
        post = self.get_post(user_id=user_id, target_date=target_date)
        if not post:
            return Response(
                {"error": "Post does not exist!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# /post/todo/<int:post_id>
class ToDoView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    @swagger_auto_schema(request_body=ToDoCreateSerializer)
    def post(self, request, post_id):
        post = self.get_post(post_id)
        # if request.user != post.user:
        #     return Response({"error": "You do not have permission to add a todo to this post."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ToDoCreateSerializer(data=request.data)
        if serializer.is_valid():
            todo = serializer.save(post=post)
            serializer = ToDoSerializer(todo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_BAD_REQUEST)

    def get(self, request, post_id):
        post = self.get_post(post_id)
        todos = post.items.all()
        serializer = ToDoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# /post/todo/<int:post_id>/<int:todo_id>
class ToDoEdit(APIView):
    # permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    @swagger_auto_schema(request_body=ToDoEditSerializer)
    def put(self, request, post_id, todo_id):
        post = self.get_post(post_id)
        try:
            todo = post.items.get(id=todo_id)
        except ToDo.DoesNotExist:
            return Response(
                {"error": "Todo item not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ToDoSerializer(todo, data=request.data, partial=True)

        if serializer.is_valid():
            todo = serializer.save()
            # update todo_progress after editing todo_item
            post.update_progress()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, todo_id):
        post = self.get_post(post_id)
        try:
            todo = post.items.get(id=todo_id)
        except ToDo.DoesNotExist:
            return Response(
                {"error": "Todo item not found."}, status=status.HTTP_404_NOT_FOUND
            )
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# /music/<int:post_id>
class Spotify(APIView):
    # permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
            )
        )

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    # 현재 등록된 음악 불러오기
    def get_current_song(self, post_id):
        post = self.get_post(post_id=post_id)
        return post.musics.first()

    @swagger_auto_schema(query_serializer=SpotifyQuerySerializer)
    def get(self, request, post_id):
        # get songs' list from searched results (max: 50 songs)
        query = request.query_params.get("query", None)
        if not query:
            return Response({"error": "Query parameter is required!"})

        try:
            post = self.get_post(post_id)
            results = self.sp.search(q=query, type="track", limit=50, market="KR")
            tracks = []
            for track in results["tracks"]["items"]:
                track_data = {
                    "album": track["album"]["name"],
                    "release_date": track["album"]["release_date"],
                    "singer": track["artists"][0]["name"],
                    "title": track["name"],
                    "song_url": track[
                        "preview_url"
                    ],  # spotify에서 불러올때 None 값이 존재함
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

    @swagger_auto_schema(request_body=SongCreateSerializer)
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 등록된 음악을 변경할 경우
    @swagger_auto_schema(request_body=SongCreateSerializer)
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


# /timer/<int:post_id>
class TimerView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    def get(self, request, post_id):
        post = self.get_post(post_id)
        # 해당 post_id 로 생성된 timer가 없을 경우
        if not hasattr(post, "timer"):
            raise NotFound(detail="Timer not found for this post.")

        timer = post.timer
        timer.update_duration()
        serializer = TimerSerializer(timer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        post = self.get_post(post_id)
        serializer = TimerCreateSerializer(data=request.data)
        if serializer.is_valid():
            timer = serializer.save(post=post, on_btn=True)
            serializer = TimerSerializer(timer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_BAD_REQUEST)

    # timer reset/pause/restart
    @swagger_auto_schema(request_body=TimerActionSerializer)
    def patch(self, request, post_id):
        action = request.data.get("action", None)
        post = self.get_post(post_id)
        timer = post.timer
        if action == "pause":
            timer.pause()
        elif action == "restart":
            timer.restart()
        elif action == "reset":
            timer.reset()
        else:
            return Response(
                {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(TimerSerializer(timer).data, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        post = self.get_post(post_id)
        timer = post.timer
        timer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
