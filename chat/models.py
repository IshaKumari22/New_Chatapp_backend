from django.db import models
from django.contrib.auth.models import User

class Thread(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"

    def get_receiver(self, sender):
        """
        Helper method to automatically get the receiver based on the sender.
        """
        if sender == self.user1:
            return self.user2
        elif sender == self.user2:
            return self.user1
        else:
            return None


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.content[:20]}"
