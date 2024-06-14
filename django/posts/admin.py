from django.contrib import admin
from posts.models import Post, Music, Timer, ToDo, UserGoal

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass

@admin.register(Timer)
class TimerAdmin(admin.ModelAdmin):
    pass

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    pass

@admin.register(ToDo)
class ToDoAdmin(admin.ModelAdmin):
    pass

@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    pass