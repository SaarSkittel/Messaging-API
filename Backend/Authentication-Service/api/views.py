from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.contrib.auth import authenticate
from .tasks import register_task
from .jwt import get_tokens_for_user
# Create your views here.
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

#Async
@api_view(["POST"])
def register(request):
    #try:
    username=request.data["username"]
    email=request.data["email"]
    password=request.data["password"]
    try:
        if  not username and not email and not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        task = register_task.apply_async(args=(username, email, password))
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)