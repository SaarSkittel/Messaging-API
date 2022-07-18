from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .tools import update_unread,update_list_unread,delete,write
from .jwt import get_tokens_for_user,get_user_from_token,refresh_access_token,verify_refresh_token
from rest_framework import status
from django.conf import settings
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from datetime import datetime
from rest_framework_simplejwt.exceptions import TokenError

@api_view(["POST"])
def write_message(request):
    now = datetime.now()
    data={
        "sender":None,
        "receiver":None,
        "subject":request.data["subject"],
        "message":request.data["message"],
        "creation_date":now.strftime("%Y-%m-%d"),
        "unread":True
    }
   
    try:
        sender=User.objects.get(id=get_user_from_token(request.headers["Authorization"]))
        receiver=User.objects.get(id=request.data["receiver"])
        if not receiver or not sender:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data["sender"]=str(sender)
        data["receiver"]=str(receiver)
        write(sender,receiver,data)
        data["uread"]=False
        write(receiver,sender,data)    
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  

@api_view(["GET"])
def get_all_messages(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("id")
    try:
        user=User.objects.get(id=current_user)
        conversations= user.conversation_set.get(friend=user_conversation)
        messages=conversations.message_set.all()
        print("test")
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    update_unread(messages)
    return Response(list(messages.values()))

@api_view(["GET"])
def get_all_unread_messages(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("id")
    try:
        user=User.objects.get(id=current_user)
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
    user_conversation=request.GET.get("id")
    try:
        user=User.objects.get(id=current_user)
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
        delete(current_user,user_conversation,message_position)
        delete(user_conversation,current_user,message_position)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return Response(status=status.HTTP_200_OK)

@api_view(["POST"])
def authentication(request):
    user_name=request.data["username"]
    user_password=request.data["password"]
    if not user_name or not user_password:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
       user = authenticate(username=user_name, password=user_password)
       if user is not None:
            response=Response()
            tokens=get_tokens_for_user(user)
            response.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'],  
                    value = tokens["refresh"],
                    expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
            
            response.data={"access_token":tokens["access"]}
            print("test2")
            return response
       else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied:
         return Response(status=status.HTTP_403_FORBIDDEN)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def register(request):
    username=request.data["username"]
    email=request.data["email"]
    password=request.data["password"]
    if  not username and not email and not password:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.create_user(username, email, password )
        user.save()
        return Response(status=status.HTTP_201_CREATED)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(["GET"])
def test(request):

    current_user=2
    user_conversation=3
    try:
        user=User.objects.get(id=current_user)
        conversations= user.conversation_set.get(friend=user_conversation)
        messages=conversations.message_set.all()
        print("test")
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    update_unread(messages)
    return Response(list(messages.values()))

@api_view(["POST"])
def token(request):
    try:
        refresh_token=request.COOKIES["REFRESH_TOKEN"]
        if refresh_token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        verify_refresh_token(refresh_token)
        access_token=refresh_access_token(refresh_token)
        print(f'token:{access_token}')
        return Response(status=status.HTTP_200_OK,data={"access_token":str(access_token)})
    except TokenError:
        return Response(status=status.HTTP_403_FORBIDDEN)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)