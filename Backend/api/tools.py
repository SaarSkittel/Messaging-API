from django.contrib.auth.models import User

def update_unread(messages):
    for message in messages:
        message.change_unread()
        message.save()
    
    
def update_list_unread(messages):
    for message in messages:
        message["unread"]= False
    

def delete(id1, id2, position):
    print(id1,id2)
    user=User.objects.get(id=id1)
    conversation=user.conversation_set.get(friend=id2)
    conversation.message_set.filter(sort=position).delete()
    
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
    