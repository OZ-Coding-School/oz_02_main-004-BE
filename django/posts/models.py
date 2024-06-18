from django.db import models
from common.models import CommonModel
from django.core.validators import URLValidator
from users.models import User
from django.utils import timezone
from datetime import timedelta
from pets.models import SnackType, Snack

# Use Django signals to automatically update future posts when the user's goal or d-day changes
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class UserGoal(CommonModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='goal')
    goal = models.CharField(max_length=255, blank=True, null=True)
    d_day = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.nickname}'s goal"

    def update_future_posts(self):
        today = timezone.now().date()
        posts = Post.objects.filter(user=self.user, todo_date__gte=today)

        if self.d_day is not None:
            posts_to_none = posts.filter(todo_date__gt=self.d_day)
            posts = posts.filter(todo_date__lte=self.d_day)
        else:
            posts_to_none = Post.objects.none()  # empty queryset

        # 각 쿼리셋 한꺼번에 업데이트
        posts_to_none.update(goal=None, d_day=None)
        posts.update(goal=self.goal, d_day=self.d_day)


class Post(CommonModel):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    feeling_status = models.PositiveSmallIntegerField(null=True, blank=True)
    todo_progress = models.PositiveIntegerField(default=0)
    todo_date = models.DateField(default=timezone.now)
    memo = models.TextField(blank=True, null=True)

    # goal settings
    goal = models.CharField(max_length=255, blank=True, null=True)
    d_day = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'ID: {self.id}, date: {self.todo_date}'

    def update_progress(self):
        num_items = self.items.all().count()
        if num_items:
            num_done = self.items.filter(done=True).count()
            self.todo_progress = int((num_done / num_items) * 100)
            self.save(update_fields=['todo_progress'])

            # 80 프로 이상 todo 완료시 하루 한번 펫에게 밥주기
            if self.todo_progress >= 80:
                self.give_rice_to_pet()

        else:
            self.todo_progress = 0
            self.save(update_fields=['todo_progress'])

    @property
    def days_by_deadline(self):
        if self.d_day:
            return (self.d_day - self.todo_date).days
        return None

    def is_overdue(self):
        if self.d_day:
            return self.todo_date > self.d_day
        return False

    # 펫에게 밥주기 기능
    def give_rice_to_pet(self):
        pet = self.user.pet
        if pet.last_snack_date != self.todo_date:
            snack_type = SnackType.objects.get(name='rice')
            snack, created = Snack.objects.get_or_create(pet=pet, snack_type=snack_type)
            snack.quantity += 1
            snack.save()

            pet.last_snack_date = self.todo_date
            pet.save(update_fields=['last_snack_date'])


# new post 객체를 db에 저장하기 전에
# usergoal table 로 부터 goal과 d-day를 상속받도록 한다
@receiver(pre_save, sender=Post)
def set_goal_and_d_day(sender, instance, **kwargs):
    # check if the post is being created
    # user_goal: usergoal instance
    user_goal = getattr(instance.user, 'goal', None)
    if user_goal:
        # post instance:  goal field, d-day fields update
        instance.goal = user_goal.goal
        instance.d_day = user_goal.d_day


# automatically update posts(from today to the future date)
# when user's goal or d-day changes
@receiver(post_save, sender=UserGoal)
def update_posts_goal(sender, instance, **kwargs):
    instance.update_future_posts()


# UserGoal object is created when a new user is registered:
@receiver(post_save, sender=User)
def create_user_goal(sender, instance, created, **kwargs):
    if created:
        UserGoal.objects.create(user=instance)


class ToDo(CommonModel):
    todo_item = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return f'Item : {self.todo_item} Done : {self.done}'


class Music(CommonModel):
    singer = models.CharField(max_length=255, default='')
    album = models.CharField(max_length=255, default='')
    title = models.CharField(max_length=255, null=False)
    release_date = models.DateField(blank=True, null=True)
    song_url = models.CharField(max_length=255, blank=True, null=True, validators=[URLValidator()])
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='music')

    def __str__(self):
        return f'Title: {self.title}, POST: {self.post.id}'


class Timer(CommonModel):
    on_btn = models.BooleanField(default=False)
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(default=timedelta)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='timer', null=True, blank=True)

    def __str__(self):
        return f'Post: {self.post}, On/off: {self.on_btn}, Duration: {self.duration}'

    def pause(self):
        self.on_btn = False
        self.end = timezone.now()
        self.update_duration()
        self.save()

    def restart(self):
        self.on_btn = True
        self.start = timezone.now()
        self.end = None
        self.save()

    def reset(self):
        self.on_btn = False
        self.end = None
        self.duration = timedelta()
        self.start = timezone.now()
        self.save()

    def update_duration(self):
        if self.end:
            self.duration += self.end - self.start
        else:
            self.duration += timezone.now() - self.start

    def format_duration(self):
        total_seconds = int(self.duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'