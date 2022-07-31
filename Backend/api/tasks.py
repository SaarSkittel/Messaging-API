import time
from server.celery import app

@app.task
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return "Fuck Yeah!"