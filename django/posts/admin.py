from django.contrib import admin
from posts.models import Post, Music, Timer


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # # display fields
    # list_display = ["question_id", "question_content", "is_active"]
    # # created_at descending order
    # ordering = ("question_id",)
    pass


@admin.register(Timer)
class TimerAdmin(admin.ModelAdmin):
    pass


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    pass