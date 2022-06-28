from distutils.log import error
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_user_from_token(token):
    try:
        access_token=AccessToken(token=token, verify=False)
        return access_token.get(key="user_id")
    except error:
        raise error

## use in middleware
def verify_access_token(token):
    try:
        access_token=AccessToken(token=token, verify=True)
    except error:
        raise error ## raise error if verification failed

def verify_refresh_token(token):
    try:        
        refresh_token=RefreshToken(token=token, verify=True)
    except error:
        raise error ## raise error if verification failed