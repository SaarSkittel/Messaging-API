from django.contrib.auth.models import User
from datetime import datetime

def register(username,email,password):
    user = User.objects.create_user(username,email,password)
    user.save()

    
