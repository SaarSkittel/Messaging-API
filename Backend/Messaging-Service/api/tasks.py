import time
from typing import Dict
from server.celery import app
from .queries import write_message,get_all_messages,get_all_unread_messages,register,delete_message,read_message
from celery import shared_task


@shared_task
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return "Fuck Yeah!"

@shared_task
def get_all_messages_task(token,id):
    data=get_all_messages(token,id)
    return data

@shared_task
def get_all_unread_messages_task(token,id):
    data=get_all_unread_messages(token,id)
    return data

@shared_task
def delete_message_task(token,id,message_position):
    delete_message(token,id,message_position)
    return True

@shared_task
def read_message_task(token,id):
    data=read_message(token,id)
    return data

@shared_task
def write_message_task(token, id, data):
    write_message(token, id, data)
    return True
"""
@shared_task
def register_task(username,email, password):
    register(username,email,password)
    return True
"""
