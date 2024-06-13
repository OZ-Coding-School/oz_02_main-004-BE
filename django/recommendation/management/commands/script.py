from django.core.management.base import BaseCommand
from users.models import User
from posts.models import Post, ToDo
from recommendation.models import UserToDoInteraction
import random
from django.utils import timezone
from faker import Faker

class Command(BaseCommand):
    help = 'Creates users, ToDo items, and interactions'

    def handle(self, *args, **kwargs):

        fake = Faker()

        # 사용자 생성
        users = []
        for _ in range(100):
            user = User.objects.create_user(nickname=fake.user_name(), email=fake.email(), password='petodo1234',)
            users.append(user)

        # Post 생성
        posts = []
        for user in users:
            post = Post.objects.create(user=user, todo_date=timezone.now().date(), memo=f'Memo for user {user.username}',)
            posts.append(post)

        # ToDo 항목 생성
        categories = ['Work', 'Personal', 'Health', 'Finance', 'Education']
        todo_items = []
        for i, post in enumerate(posts):
            for j in range(2):  # Creating 2 ToDo items per post
                todo = ToDo.objects.create(post=post, todo_item=f'ToDo {i*2 + j}', done=random.choice([True, False]),)
                todo_items.append(todo)

        # 사용자와 ToDo 항목 간의 상호작용 생성
        interaction_types = ['completed', 'liked']
        for user in users:
            for todo in random.sample(todo_items, 10):  # 각 사용자당 10개의 랜덤 ToDo 항목과 상호작용
                UserToDoInteraction.objects.create(user=user, todo=todo, interaction_type=random.choice(interaction_types),)

        self.stdout.write(self.style.SUCCESS('Successfully created users, ToDo items, and interactions'))