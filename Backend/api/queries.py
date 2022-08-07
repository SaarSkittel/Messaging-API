from django.contrib.auth.models import User
from .models import Conversation,Message
from .serializers import MessageSerializer
from .jwt import get_user_from_token
from datetime import datetime

def register(username,email,password):
    user = User.objects.create_user(username,email,password)
    user.save()

def write_message(token, id, data):
    sender=User.objects.get(id=get_user_from_token(token))
    receiver=User.objects.get(id=id)
    now = datetime.now().strftime("%Y-%m-%d")    
    data["sender"]=str(sender)
    data["receiver"]=str(receiver)
    data["creation_date"]=now
    write(sender,receiver,data)
    data["uread"]=False
    write(receiver,sender,data)    

def read_message(token, id):
    current_user=get_user_from_token(token)
    message=Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=current_user, conversation__friend=id).order_by("sort").last()
    message.change_unread()
    message.save()
    serializer=MessageSerializer(message)
    return serializer.data

def update_unread(messages):
    for message in messages:
        if message.unread:
            message.change_unread()
            message.save()


def get_all_messages(token,id):
    current_user=get_user_from_token(token)
    messages=Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=current_user, conversation__friend=id)
    update_unread(messages)
    serializer=MessageSerializer(messages,many=True)
    return serializer.data

def get_all_unread_messages(token,id):
    current_user=get_user_from_token(token)
    messages=Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=current_user, conversation__friend=id, unread=True)
    result=list(messages.values()).copy()
    update_list_unread(result)
    serializer=MessageSerializer(messages,many=True)
    update_unread(messages)
    return serializer.data

def delete_message(token, id, message_position):
    current_user=get_user_from_token(token)
    delete(current_user,id,message_position)
    delete(id,current_user,message_position)


def update_list_unread(messages):
    for message in messages:
        if message["unread"]:
            message["unread"]= False
    

def delete(id1, id2, position):
    Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=id1, conversation__friend=id2, sort=position).delete()

def write(user1,user2, data):
    try:
        friend=user1.conversation_set.get(friend=user2.id)
        last_message=friend.message_set.order_by("sort").last()
        sort=last_message.sort+1
        friend.message_set.create(sort=sort,sender=data["sender"],receiver=data["receiver"],subject=data["subject"],message=data["message"],date=data["creation_date"],unread=data["unread"])
    except Conversation.DoesNotExist:
        user1.conversation_set.create(friend=user2.id)
        sort=1
        friend=user1.conversation_set.get(friend=user2.id)
        friend.message_set.create(sort=sort,sender=data["sender"],receiver=data["receiver"],subject=data["subject"],message=data["message"],date=data["creation_date"],unread=data["unread"])
    except:
        raise "Internal Server Error"
    
    
