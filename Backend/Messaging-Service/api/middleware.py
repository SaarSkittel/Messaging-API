from .jwt import verify_access_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class Middleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self, request):
        response=self.get_response(request) 
        return response 
        
    def process_view(self,request,view_func,view_args,view_kargs):
        paths=["/api/auth/","/api/register/","/api/token/","/api/test"]
        if request.path not in paths and "/admin/" not in request.path and "/__debug__/" not in request.path and "/status/" not in request.path:
            print("test")
            if not request.headers.get("Authorization"):
                response = Response(
                    status=status.HTTP_400_BAD_REQUEST
                    )
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                return response
            try:
                
                result=verify_access_token(request.headers["Authorization"])
                
            except:
                response = Response(
                    status=status.HTTP_401_UNAUTHORIZED
                    )
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                return response
        
        
        