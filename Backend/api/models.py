from django.db import models
from django.contrib.auth.models import User
# Create your models here.
"""
class User(models.Model):
    name=models.CharField(max_length=200, null=False,default="")
    password=models.CharField(max_length=20, null=False,default="")
    def __str__(self) -> str:
        return self.name
"""
class Conversation(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    friend=models.CharField(max_length=200)
    def __str__(self) -> str:
        return self.friend

class Message(models.Model):
    user=models.ForeignKey(Conversation,on_delete=models.CASCADE)
    sort=models.IntegerField(default=None)
    sender=models.CharField(max_length=200)
    receiver=models.CharField(max_length=200)
    subject=models.CharField(max_length=200)
    message=models.CharField(max_length=10000)
    date=models.DateField()
    unread=models.BooleanField()
    def change_unread(self):
        self.unread=False

