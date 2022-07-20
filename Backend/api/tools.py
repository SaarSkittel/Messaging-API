from django.contrib.auth.models import User
from .models import Conversation,Message

def update_unread(messages):
    for message in messages:
        print (message.unread)
        if message.unread:
            message.change_unread()
            message.save()
    
    
def update_list_unread(messages):
    for message in messages:
        if message["unread"]:
            message["unread"]= False
    

def delete(id1, id2, position):
    Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=id1, conversation__friend=id2, sort=position).delete()


"""
def write(user1, user2, data):
    if not user1.conversation_set.filter(friend=user2.id).exists():
        user1.conversation_set.create(friend=user2.id)
        sort=1
    else:
        friend=user1.conversation_set.get(friend=user2.id)
        last_message=friend.message_set.order_by("sort").last()
        sort=last_message.sort+1
    
    friend=user1.conversation_set.get(friend=user2.id)
    friend.message_set.create(sort=sort,sender=data["sender"],receiver=data["receiver"],subject=data["subject"],message=data["message"],date=data["creation_date"],unread=data["unread"])
    
"""
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
    
    
