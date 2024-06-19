from django.conf import settings
from posts.models import Post, ToDo, UserGoal, Music
from users.userviews import IsStaffUser
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from posts.serializer import (
    PostSerializer, PostCreateSerializer, PostDeleteSerializer, SpotifySerializer, SongCreateSerializer, SpotifyQuerySerializer,
    SpotifySearchSerializer, TimerSerializer, TimerCreateSerializer, TimerActionSerializer, ToDoSerializer, ToDoEditSerializer,
    ToDoCreateSerializer, ConsecutiveDaysSerializer, UserGoalSerializer,
)
from drf_yasg.utils import swagger_auto_schema

# spotify reference : https://spotipy.readthedocs.io/en/2.24.0/#examples
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# get consecutive days when todo_progress > = 80
from posts.utils import get_consecutive_success_days


# /api/v1/posts/goal
class UserGoalView(APIView):
    # only logined user are allowed to get an access
    permission_classes = [IsAuthenticated]

    def get_user(self, request):
        return request.user

    def get(self, request):
        '''
        Retrieve the goal for the authenticated user.
        '''
        user = self.get_user(request)
        goal = getattr(user, 'goal', None)
        serializer = UserGoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserGoalSerializer)
    def post(self, request):
        '''
        Create or update the goal for the authenticated user.
        '''
        user = self.get_user(request)
        goal, _ = UserGoal.objects.get_or_create(user=user)
        serializer = UserGoalSerializer(goal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Serialize again to include the updated goal with days_by_deadline
            response_serializer = UserGoalSerializer(goal)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# /api/v1/posts/calendar/
class CalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, request):
        return request.user

    def get(self, request):
        '''
        Retrieve the streak of consecutive successful days.
        '''
        user = self.get_user(request)
        streak = get_consecutive_success_days(user)
        serializer = ConsecutiveDaysSerializer(data={'streak': streak})

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# /api/v1/posts/list
class PostList(APIView):
    # 관리자만 접근 가능
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get(self, request):
        '''
        Retrieve a list of all posts (accessible by staff users only).
        '''
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# /api/v1/posts
class PostsByUser(APIView):
    # todo: 로그인한 해당 유저만 접근가능
    permission_classes = [IsAuthenticated]

    def get_user(self, request):
        return request.user

    # get post list written by a certain user
    def get_posts_by_user(self, request):
        user = self.get_user(request)
        return Post.objects.filter(user=user)

    # get the post written on a certain day by user
    def get_post(self, request, target_date):
        user = self.get_user(request)
        return Post.objects.filter(user=user, todo_date=target_date).first()

    def get(self, request):
        '''
        Retrieve a list of posts created by the authenticated user.
        '''
        posts = self.get_posts_by_user(request)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PostCreateSerializer)
    def post(self, request):
        '''
        Create a new post for the authenticated user.
        '''
        user = self.get_user(request)
        serializer = PostCreateSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            post = serializer.save()  # Save with the user
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 포스트 내용 변경 : 'todo_date' is required
    @swagger_auto_schema(request_body=PostCreateSerializer)
    def put(self, request):
        '''
        Update a post created by the authenticated user on a specific date.
        '''
        user = self.get_user(request)
        target_date = request.data.get('todo_date')
        post = self.get_post(request, target_date=target_date)
        if not post:
            return Response({'error': 'Post Not Found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PostSerializer(post, data=request.data, partial=True, context={'user': user})
        if serializer.is_valid():
            post = serializer.save()
            post_serializer = PostSerializer(post)
            return Response(post_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 포스트 삭제 : 'todo_date' is required
    @swagger_auto_schema(request_body=PostDeleteSerializer)
    def delete(self, request):
        '''
        Delete a post created by the authenticated user on a specific date.
        '''
        user = self.get_user(request)
        target_date = request.data.get('todo_date')
        post = self.get_post(request, target_date=target_date)
        if not post:
            return Response({'error': 'Post does not exist!'}, status=status.HTTP_404_NOT_FOUND,)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# /api/v1/posts/todo/<int:post_id>
class ToDoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    @swagger_auto_schema(request_body=ToDoCreateSerializer)
    def post(self, request, post_id):
        '''
        Create a new to-do item for a specific post.
        '''
        post = self.get_post(post_id)

        if request.user != post.user:
            return Response({'error': 'You do not have permission to add a todo to this post.'}, status=status.HTTP_403_FORBIDDEN,)

        serializer = ToDoCreateSerializer(data=request.data)
        if serializer.is_valid():
            todo = serializer.save(post=post)
            serializer = ToDoSerializer(todo)
            # update todo_progress after editing todo_item
            post.update_progress()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_BAD_REQUEST)

    def get(self, request, post_id):
        '''
        Retrieve the to-do items for a specific post.
        '''
        post = self.get_post(post_id)
        todos = post.items.all().order_by('created_at')  # ascending order
        serializer = ToDoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# /api/v1/posts/todo/<int:post_id>/<int:todo_id>
class ToDoEdit(APIView):
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    @swagger_auto_schema(request_body=ToDoEditSerializer)
    def put(self, request, post_id, todo_id):
        '''
        Update a to-do item for a specific post.
        '''
        post = self.get_post(post_id)
        try:
            todo = post.items.get(id=todo_id)
        except ToDo.DoesNotExist:
            return Response({'error': 'Todo item not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ToDoSerializer(todo, data=request.data, partial=True)

        if serializer.is_valid():
            todo = serializer.save()
            # update todo_progress after editing todo_item
            post.update_progress()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, todo_id):
        '''
        Delete a to-do item for a specific post.
        '''
        post = self.get_post(post_id)
        try:
            todo = post.items.get(id=todo_id)
        except ToDo.DoesNotExist:
            return Response({'error': 'Todo item not found.'}, status=status.HTTP_404_NOT_FOUND)
        todo.delete()
        post.update_progress()
        return Response(status=status.HTTP_204_NO_CONTENT)


# /api/v1/posts/music/<int:post_id>
class Spotify(APIView):
    permission_classes = [IsAuthenticated]

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

    def get_current_song(self, post_id):
        try:
            post = self.get_post(post_id=post_id)
            return post.music
        except Music.DoesNotExist:
            return None

    @swagger_auto_schema(query_serializer=SpotifyQuerySerializer)
    def get(self, request, post_id):
        '''
        Get a list of songs based on the query parameter from Spotify API.
        '''
        query = request.query_params.get('query', None)
        if not query:
            return Response({'error': 'Query parameter is required!'}, status=status.HTTP_400_BAD_REQUEST,)

        try:
            post = self.get_post(post_id)
            results = self.sp.search(q=query, type='track', limit=50, market='KR')
            tracks = []
            for track in results['tracks']['items']:
                track_data = {
                    'album': track['album']['name'],
                    'release_date': track['album']['release_date'],
                    'singer': track['artists'][0]['name'],
                    'title': track['name'],
                    'song_url': track.get('preview_url', None),
                }
                serializer = SpotifySearchSerializer(data=track_data)
                if serializer.is_valid():
                    tracks.append(serializer.validated_data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(tracks, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=SongCreateSerializer)
    def post(self, request, post_id):
        '''
        Add a new song to the post.
        data = {
            'album': 'abc',
            'release_date': '2018-08-24',
            'singer': 'BTS',
            'title': 'akdjkj',
            'song_url':'url',
        }
        '''
        post = self.get_post(post_id=post_id)
        serializer = SongCreateSerializer(data=request.data)

        if serializer.is_valid():
            # check if a music instance already exists for the post
            current_song = self.get_current_song(post_id=post_id)
            if current_song:
                # update the current song
                serializer = SpotifySerializer(current_song, data=request.data, partial=True)
                if serializer.is_valid():
                    song = serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:
                # create a new song
                song = serializer.save(post=post)
                serializer = SpotifySerializer(song)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        '''
        Delete the current song from the post.
        '''
        current_song = self.get_current_song(post_id=post_id)
        if not current_song:
            return Response({'error': 'No song exists'}, status=status.HTTP_404_NOT_FOUND,)
        current_song.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# /api/v1/posts/music/playing/<int:post_id>
class MusicView(APIView):
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    # 현재 등록된 음악 불러오기
    def get_current_song(self, post_id):
        post = self.get_post(post_id=post_id)
        return post.music

    def get(self, request, post_id):
        '''
        Get the currently registered song for the post.
        '''
        song = self.get_current_song(post_id)
        # 해당 post_id 로 생성된 timer가 없을 경우
        if not song:
            return Response({'error': 'Song not found for the post.'}, status=status.HTTP_404_NOT_FOUND,)
        serializer = SpotifySerializer(song)
        return Response(serializer.data, status=status.HTTP_200_OK)


# /api/v1/posts/timer/<int:post_id>
class TimerView(APIView):
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(Post, id=post_id)

    def get(self, request, post_id):
        post = self.get_post(post_id)
        # 해당 post_id 로 생성된 timer가 없을 경우
        if not hasattr(post, 'timer'):
            raise NotFound(detail='Timer not found for this post.')

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
        action = request.data.get('action', None)
        post = self.get_post(post_id)
        timer = post.timer
        if action == 'pause':
            timer.pause()
        elif action == 'restart':
            timer.restart()
        elif action == 'reset':
            timer.reset()
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TimerSerializer(timer).data, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        post = self.get_post(post_id)
        timer = post.timer
        timer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)