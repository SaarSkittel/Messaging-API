import time
from server.celery import app
from .queries import write_message,get_all_messages,get_all_unread_messages,register,delete_message,read_message
@app.task
def create_task(task_type):
    print("test")
    time.sleep(int(task_type) * 10)
    return "Fuck Yeah!"

@app.task(name="get_all_messages_task")
def get_all_messages_task(token,id):
    data=get_all_messages(token,id)
    return data

@app.task(name="get_all_unread_messages_task")
def get_all_unread_messages_task(token,id):
    data=get_all_unread_messages(token,id)
    return data

@app.task(name="delete_message_task")
def delete_message_task(token,id,message_position):
    delete_message(token,id,message_position)
    return True

@app.task(name="read_message_task")
def read_message_task(token,id):
    data=read_message(token,id)
    return data

@app.task("write_message_task")
def write_message_task(token, id, data):
    write_message(token, id, data)
    return True

@app.task(name="register_task")
def register_task(user_data):
    register(user_data)
    return True

