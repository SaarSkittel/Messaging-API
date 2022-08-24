# Messaging-API
## Introduction
Messaging RESTful API developed in Python using Django Rest Framework. 

Stack- Django, Django rest Framework, Celery, Celery Flower, Redis, SQLite and DJDT.

## API requests

• Write Message- Sends a message to specified user.

• Read Message- Read the last message from a specied user.

• Delete Message- Deletes a nessage from the users conversations.

• Get All Messages- Get all messages from specied user.

• Get Unread Messages-Get all unread messages from specied user.

• Authentication- Authenticate username and password and returns access token and refresh token.

• Register- Signs a new user to the system.

• Token- Refresh a new access token.


## Technologies used

• SimpleJWT- The requests that are sent to the server are authenticated by with both access token and refresh token to ensure fraud and identity theft. The access token is given to the user when he logs in it has an expiration time of an 5 minutes the user gets it in the response or when he request to refresh it when it is expired.
The refresh token is also given when the user logs in and it is stored in the cookies as an HttpOnly so the refresh token only visible to the server.

• SQLite- Handles all conversations,messages and users data using Django bulit-in user system and custom models. Optinized queries using select_related to minimize the amout of SQL queries needed for a singke action.  

• DJDT- Used to optimize requests queries and maximize response time of requests. 

• Middleware- Middleware was used to insure tokens validation before executing requests.

• Celery- Creatad Celery worker to make the API requests and resppnse work Asynchronous.

• Celery Flower- Monitors the Celery worker and tasks.

• Redis- Used as Celery Broker to store results from tasks.

