from django.db import models
from common.models import CommonModel
from django.core.validators import URLValidator
from users.models import User
from django.utils import timezone
from datetime import timedelta


class Post(CommonModel):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    feeling_status = models.PositiveSmallIntegerField(null=True, blank=True)
    todo_progress = models.PositiveIntegerField(default=0)
    todo_date = models.DateField(default=timezone.now)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"ID: {self.id}, date: {self.todo_date}"


class ToDo(CommonModel):
    pass


class Music(CommonModel):
    singer = models.CharField(max_length=255, default="")
    album = models.CharField(max_length=255, default="")
    title = models.CharField(max_length=255, null=False)
    release_date = models.DateField(blank=True, null=True)
    song_url = models.CharField(
        max_length=255, blank=True, null=True, validators=[URLValidator()]
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="musics")

    def __str__(self):
        return f"Title: {self.title}, POST: {self.post.id}"


class Timer(CommonModel):
    on_btn = models.BooleanField(default=False)
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(default=timedelta)
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="timer", null=True, blank=True
    )

    def __str__(self):
        return f"Post: {self.post}, On/off: {self.on_btn}, Duration: {self.duration}"

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

        # Reset start to prepare for next duration update
        # self.start = timezone.now()
