from django.db import models
from django.contrib.auth.models import User

class Thread(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_user2')
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # ← add this
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
