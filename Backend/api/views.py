import email
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Conversation,Message
from django.contrib.auth.models import User
from .tools import update_unread,update_list_unread
from .jwt import get_tokens_for_user,get_user_from_token
from rest_framework import status
from django.forms.models import model_to_dict
@api_view(["POST"])
def write_message(request):
    sender=get_user_from_token(request.headers["Authorization"])
    receiver=request.data["receiver"]
    subject=request.data["subject"]
    message=request.data["message"]
    creation_date=request.data["creation date"]
    try:
        m_sender=User.objects.get(name=sender)
        m_receiver=User.objects.get(name=receiver)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if not m_receiver.conversation_set.filter(friend=sender).exists():
        m_receiver.conversation_set.create(friend=sender)
        sort=1
    else:
        friend=m_receiver.conversation_set.get(friend=sender)
        last_message=friend.message_set.order_by("sort").last()
        sort=last_message.sort+1
    friend=m_receiver.conversation_set.get(friend=sender)
    friend.message_set.create(sort=sort,sender=sender,receiver=receiver,subject=subject,message=message,date=creation_date,unread=True)

    if not m_sender.conversation_set.filter(friend=receiver).exists():
        m_sender.conversation_set.create(friend=receiver)
    friend=m_sender.conversation_set.get(friend=receiver)
    friend.message_set.create(sort=sort,sender=sender,receiver=receiver,subject=subject,message=message,date=creation_date,unread=False)
        
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_all_messages(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("name")
    try:
        user=User.objects.get(name=current_user)
        conversations= user.conversation_set.get(friend=user_conversation)
        messages=conversations.message_set.all()
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    update_unread(messages)
    return Response(list(messages.values()))

@api_view(["GET"])
def get_all_unread_messages(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("name")
    try:
        user=User.objects.get(name=current_user)
        conversations= user.conversation_set.get(friend=user_conversation)
        messages=conversations.message_set.filter(unread=True)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    result=list(messages.values()).copy()
    update_list_unread(result)
    update_unread(messages)
    return Response(result)
    

@api_view(["GET"])
def read_message(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("name")
    try:
        user=User.objects.get(name=current_user)
        conversations= user.conversation_set.get(friend=user_conversation)
        message=conversations.message_set.order_by("sort").last()
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    message.change_unread()
    message.save()
    return Response(model_to_dict(message))

@api_view(["DELETE"])
def delete_message(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.data["user_conversation"]
    try:
        message_position=request.data["sort"]
        user=User.objects.get(name=current_user)
        conversation=user.conversation_set.get(friend=user_conversation)
        conversation.message_set.filter(sort=message_position).delete()

        user=User.objects.get(name=user_conversation)
        conversation=user.conversation_set.get(friend=current_user)
        conversation.message_set.filter(sort=message_position).delete()
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return Response(status=status.HTTP_200_OK)

@api_view(["POST"])
def authentication(request):
    print(request.data)
    user_name=request.data["username"]
    user_password=request.data["password"]
    
    if not user_name or not user_password:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        user=User.objects.get(name=user_name)
    except:
        ## CAN BE BOTH INTERNAL ERROR AND USER NOT EXIST
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if user.password==user_password:
        return Response(get_tokens_for_user(user_name))
    else:
        pass
        #return response with incorrect password
        return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(["GET"])
def register(request):
    username=request.GET.get("username")
    password=request.GET.get("password")
    
