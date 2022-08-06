import imp
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .tasks import *
from .queries import all_messages, all_unread_messages, message_delete,read_last_message,message_write,create_user
from .jwt import get_tokens_for_user,refresh_access_token,verify_refresh_token
from rest_framework import status
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError
from celery.result import AsyncResult
from .tasks import *


### DONE ###
# async
@api_view(["GET"])
def get_all_messages(request):
    try:
        token=request.headers["Authorization"]
        id=request.GET.get("id")
        ## data=all_messages(token,id)
        ## return Response(data)
        task = get_all_messages_task.delay(token,id)
        return Response(data={"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    

# async
@api_view(["GET"])
def get_all_unread_messages(request):    
    try:
        token=request.headers["Authorization"]
        id=request.GET.get("id")
       ## data= all_unread_messages(token,id)
       ## return Response(data)
        task = get_all_unread_messages_task.delay(token,id)
        return Response(data={"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
# async
@api_view(["DELETE"])
def delete_message(request):
    try:
        token=request.headers["Authorization"]
        id=request.data["user_conversation"]
        message_position=request.data["sort"]
        ##message_delete(token, id, message_position)
        ##return Response(status=status.HTTP_200_OK)
        task = delete_message_task.delay(token,id)
        return Response(data={"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# async
@api_view(["GET"])
def read_message(request):
    try:
        token=request.headers["Authorization"]
        id=request.GET.get("id")
        ##data=read_last_message(token, id)
        ##return Response(data)
        task = read_message_task.delay(token,id)
        return Response(data={"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# async
@api_view(["POST"])
def write_message(request):
    try:
        token=request.headers["Authorization"]
        id=request.data["receiver"]
        data={  
            "sender":None,
            "receiver":None,
            "subject":request.data["subject"],
            "message":request.data["message"],
            "creation_date":None,
            "unread":True
        }
        ##message_write(token,id,data)
        ##return Response(status=status.HTTP_200_OK)
        task = write_message_task.delay(token,id)
        return Response(data={"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Async
@api_view(["POST"])
def register(request):
    try:
        user_data={
            "username":request.data["username"],
            "email":request.data["email"],
            "password":request.data["password"]
        }

        if  not user_data["username"] and not user_data["email"] and not user_data["password"]:
            return Response(status=status.HTTP_400_BAD_REQUEST)
       
        ##create_user(user_data)
        ##return Response(status=status.HTTP_201_CREATED)
        task = register_task.delay(user_data)
        return Response(data={"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

### TO DO ###

# Multithreaded
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
            
            return response
       else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied:
         return Response(status=status.HTTP_403_FORBIDDEN)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Multithreaded
@api_view(["POST"])
def token(request):
    try:
        refresh_token=request.COOKIES["REFRESH_TOKEN"]
        if refresh_token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        verify_refresh_token(refresh_token)
        access_token=refresh_access_token(refresh_token)
        return Response(status=status.HTTP_200_OK,data={"access_token":str(access_token)})
    except TokenError:
        return Response(status=status.HTTP_403_FORBIDDEN)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"]) 
def run_task(request):
    task = create_task.delay(1)
    return Response(data={"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

@api_view(["GET"])
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return Response(data=result, status=status.HTTP_200_OK)

### OLD VERSION ###

"""
@api_view(["GET"])
def get_all_messages(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("id")
    try:
        messages=Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=current_user, conversation__friend=user_conversation)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    update_unread(messages)
    return Response(list(messages.values()))
    

@api_view(["GET"])
def get_all_unread_messages(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("id")
    try:
        messages=Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=current_user, conversation__friend=user_conversation, unread=True)
        result=list(messages.values()).copy()
        update_list_unread(result)
        update_unread(messages)
        return Response(result)
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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

@api_view(["GET"])
def read_message(request):
    current_user=get_user_from_token(request.headers["Authorization"])
    user_conversation=request.GET.get("id")
    try:
        message=Message.objects.select_related("conversation__user","conversation").filter(conversation__user__id=current_user, conversation__friend=user_conversation).order_by("sort").last()
        message.change_unread()
        message.save()
        return Response(model_to_dict(message))
    except:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
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
        data["sender"]=str(sender)
        data["receiver"]=str(receiver)
        write(sender,receiver,data)
        data["uread"]=False
        write(receiver,sender,data)    
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    @api_view(["POST"])
def register(request):
    try:
        username=request.data["username"]
        email=request.data["email"]
        password=request.data["password"]
        if  not username and not email and not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
   
        user = User.objects.create_user(username, email, password )
        user.save()
        return Response(status=status.HTTP_201_CREATED)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """