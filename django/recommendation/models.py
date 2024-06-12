from django.db import models
from common.models import CommonModel
from users.models import User
from posts.models import ToDo

class UserToDoInteraction(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo = models.ForeignKey(ToDo, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50)  # completed,

    def __str__(self):
        return f'{self.user.username} / {self.todo.todo_item} / {self.interaction_type}'